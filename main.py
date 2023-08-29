from aiogram import Bot, Dispatcher, executor
from dotenv import load_dotenv
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3 as sql
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from keyboards import *
import os

# проверка на подписку
# user_channel_status = await bot.get_chat_member(chat_id='@localhost_sender', user_id=message.from_user.id)
# if user_channel_status["status"] != 'left'
load_dotenv()
bot = Bot(token=os.getenv("TOKEN"), parse_mode="HTML")
dp = Dispatcher(bot=bot, storage=MemoryStorage())


class WaitGetInfo(StatesGroup):
    wait_for_get_message = State()
    wait_for_get_sender_mail = State()
    wait_for_get_getter_mail = State()
    wait_for_get_header = State()


def database():
    cur.execute(
        """CREATE TABLE IF NOT EXISTS users (
        username TEXT,
        user_id INTEGER,
        start_attempts INTEGER);
        """
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS mail_info (
        sender_mail TEXT,
        getter_mail TEXT,
        message_title TEXT,
        message TEXT,
        number_of_sent INTEGER,
        user_id INTEGER);
        """
    )


with sql.connect("email.db") as con:
    cur = con.cursor()
    database()


@dp.message_handler(commands="start")
async def start_message(message: types.Message):
    username = message.from_user.first_name
    user_id = message.from_user.id
    user_channel_status = await bot.get_chat_member(chat_id='@abs1245s', user_id=user_id)
    print(user_channel_status)
    if user_channel_status["status"] != 'left':
        id_user = cur.execute(
            "SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if id_user.fetchone() is None:
            cur.execute("""INSERT INTO users (username, user_id, start_attempts) VALUES (?, ?, ?)""",
                        (username, user_id, 0))
            cur.execute("""INSERT INTO mail_info
            (sender_mail, getter_mail, message_title, message, number_of_sent, user_id) VALUES (?, ?, ?, ?, ?, ?)""",
                        ("...", "...", "...", "...", 0, user_id))
            con.commit()
        cur.execute("UPDATE users SET start_attempts = start_attempts + 1 WHERE user_id = ?", (user_id,))
        con.commit()
        start_attempts = cur.execute("SELECT start_attempts FROM users WHERE user_id = ?", (user_id,))
        if start_attempts.fetchone()[0] == 1:
            await message.answer(text=f"""
Ого, {username}, ты у нас впервые!
🌎Жми кнопку «Начать» для отправки сообщения на почту!🌏""", reply_markup=menu_keyboard)
        else:
            await message.answer(text=f"""
👋🏻{username}! Мы тебя помним!👋🏻
Чем можем помочь сегодня?""", reply_markup=menu_keyboard)
    else:
        await message.answer(text="Для начала необходимо подписаться на канал",
                             reply_markup=follow_keyboard)


async def check_subscribe(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()
    await callback.message.delete()
    user_channel_status = await bot.get_chat_member(chat_id=f'@abs1245s', user_id=user_id)
    print(user_channel_status)
    if user_channel_status["status"] != 'left':
        await callback.message.answer("""Отлично, ты подписался!✅
Теперь напиши «/start»""")
    else:
        await callback.message.answer(text="Для начала необходимо подписаться на канал. ❗️",
                                      reply_markup=follow_keyboard)


async def contacts(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer(f"""
📍<b>admin</b>: {os.getenv("ADMIN_NAME")}📍
""", reply_markup=menu_keyboard)


async def profile(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    username = callback.from_user.first_name
    user_id = callback.from_user.id
    sent_mail = cur.execute("""SELECT number_of_sent FROM mail_info WHERE user_id = ?""",
                            (user_id,)).fetchone()
    await callback.message.answer(f"""
📊 <b>PROFILE INFO</b>📊

🧊 USERNAME: <b>{username}</b> 🧊

🆔 ID: <b>{user_id}</b> 🆔

✉️ SENT MAILS: <b>{sent_mail[0]}</b> ✉️
""", reply_markup=menu_keyboard)


async def begin(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.message.delete()
    await callback.answer()
    user_channel_status = await bot.get_chat_member(chat_id=f'@abs1245s', user_id=user_id)
    print(user_channel_status)
    if user_channel_status["status"] != 'left':
        await callback.message.answer(text="Теперь введи то сообщение, которое ты хочешь передать в письме.📝")
        await state.set_state(WaitGetInfo.wait_for_get_message.state)
    else:
        await callback.message.answer(text="Для начала необходимо подписаться на канал. ❗️",
                                      reply_markup=follow_keyboard)


async def get_message(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    user_id = message.from_user.id
    cur.execute("""UPDATE mail_info SET message = ? WHERE user_id = ?""",
                (data["text"], user_id))
    con.commit()
    await state.set_state(WaitGetInfo.wait_for_get_sender_mail.state)
    await message.answer("Теперь введи почту отправителя.📪")


async def get_sender(message: types.Message, state: FSMContext):
    await state.update_data(sender_mail=message.text)
    data = await state.get_data()
    user_id = message.from_user.id
    cur.execute("""UPDATE mail_info SET sender_mail = ? WHERE user_id = ?""",
                (data["sender_mail"], user_id))
    con.commit()
    await message.answer("Теперь введи почту получателя.📤")
    await state.set_state(WaitGetInfo.wait_for_get_getter_mail.state)


async def get_getter(message: types.Message, state: FSMContext):
    await state.update_data(getter_mail=message.text)
    data = await state.get_data()
    user_id = message.from_user.id
    cur.execute("""UPDATE mail_info SET getter_mail = ? WHERE user_id = ?""",
                (data["getter_mail"], user_id))
    con.commit()
    await message.answer("✏️Теперь введи текст, который будет в заголовке сообщения.")
    await state.set_state(WaitGetInfo.wait_for_get_header.state)


async def get_header(message: types.Message, state: FSMContext):
    global user_sender_mail, user_getter_mail, user_text, user_title
    await state.update_data(title=message.text)
    data = await state.get_data()
    user_id = message.from_user.id
    cur.execute("""UPDATE mail_info SET message_title = ? WHERE user_id = ?""",
                (data["title"], user_id))
    con.commit()
    user_text = cur.execute("""SELECT message FROM mail_info WHERE user_id = ?""",
                            (user_id,)).fetchone()
    user_sender_mail = cur.execute("""SELECT sender_mail FROM mail_info WHERE user_id = ?""",
                                   (user_id,)).fetchone()
    user_getter_mail = cur.execute("""SELECT getter_mail FROM mail_info WHERE user_id = ?""",
                                   (user_id,)).fetchone()
    user_title = cur.execute("""SELECT message_title FROM mail_info WHERE user_id = ?""",
                             (user_id,)).fetchone()
    await state.finish()
    await message.answer(text=f"""Все данные правильные?
<b>message</b>: {user_text[0]}
<b>mail sender</b>: {user_sender_mail[0]}
<b>mail getter</b>: {user_getter_mail[0]}
<b>title</b>: {user_title[0]}""", reply_markup=correct_data_keyboard)


async def correct_data(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    user_id = callback.from_user.id
    try:
        if "@" in user_sender_mail[0] and "@" in user_getter_mail[0]:
            import requests as r
            response = r.post(url="https://api.scary-main.online/send_email/55.0",
                              json={
                                  "send": user_sender_mail[0],
                                  "get": user_getter_mail[0],
                                  "text": user_text[0],
                                  "subject": user_title[0]
                              })
            print(response.text)
            print(response.json()["status"])
            if response.json()["status"]:
                await callback.message.answer("Отлично! Письмо отправлено✅", reply_markup=menu_keyboard)
                cur.execute("""UPDATE mail_info SET number_of_sent = number_of_sent + 1 WHERE user_id = ?""",
                            (user_id,))
                con.commit()
            else:
                await callback.message.answer("Введенные данные неправильны.❌ Повторите ввод.🔄",
                                              reply_markup=menu_keyboard)
        else:
            await callback.message.answer("Введенные данные неправильны.❌ Повторите ввод.🔄",
                                          reply_markup=menu_keyboard)

    except Exception as ex:
        print(ex)
        await callback.message.answer("Письмо не отправлено, проверьте введенные данные.🔄")


async def not_correct_data(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("Заполните данные заново.🔄")
    await callback.message.answer("Введите сообщение, которое будет в письме.📝")
    await state.set_state(WaitGetInfo.wait_for_get_message.state)


def create_handlers():
    dp.register_callback_query_handler(callback=begin, text="begin", state="*")
    dp.register_message_handler(callback=get_message, state=WaitGetInfo.wait_for_get_message)
    dp.register_message_handler(callback=get_sender, state=WaitGetInfo.wait_for_get_sender_mail)
    dp.register_message_handler(callback=get_getter, state=WaitGetInfo.wait_for_get_getter_mail)
    dp.register_message_handler(callback=get_header, state=WaitGetInfo.wait_for_get_header)
    dp.register_callback_query_handler(callback=correct_data, text="correct", state="*")
    dp.register_callback_query_handler(callback=not_correct_data, text="not_correct", state="*")
    dp.register_callback_query_handler(callback=contacts, text="contacts", state="*")
    dp.register_callback_query_handler(callback=profile, text="profile", state="*")
    dp.register_callback_query_handler(callback=check_subscribe, text="check_subscribe", state="*")


if __name__ == "__main__":
    create_handlers()
    executor.start_polling(dp, skip_updates=True)
