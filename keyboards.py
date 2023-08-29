from aiogram import types

menu_keyboard = types.InlineKeyboardMarkup(row_width=2)
menu_keyboard.add(types.InlineKeyboardButton(text="Начать🚀", callback_data="begin"),
                  types.InlineKeyboardButton(text="Контакты🧨", callback_data="contacts"),
                  types.InlineKeyboardButton(text="Профиль📚", callback_data="profile"))
correct_data_keyboard = types.InlineKeyboardMarkup(row_width=2)
correct_data_keyboard.add(types.InlineKeyboardButton(text="Да✅", callback_data="correct"),
                          types.InlineKeyboardButton(text="Нет❌", callback_data="not_correct"))

follow_keyboard = types.InlineKeyboardMarkup(row_width=1)
follow_keyboard.add(types.InlineKeyboardButton(text="Подписаться❗️", url="https://t.me/abs1245s"),
                    types.InlineKeyboardButton(text="Проверить⚠️", callback_data="check_subscribe"))
