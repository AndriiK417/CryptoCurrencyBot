from telebot import types

currency_markup = types.InlineKeyboardMarkup()
currency_markup.row_width = 2
currency_markup.add(types.InlineKeyboardButton("<", callback_data="previous_currency"),
types.InlineKeyboardButton(">", callback_data="next_currency"))