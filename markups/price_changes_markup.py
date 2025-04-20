from telebot import types

price_changes_markup = types.InlineKeyboardMarkup()
price_changes_markup.row_width = 2
price_changes_markup.add(
    types.InlineKeyboardButton("<", callback_data="previous_price_changes"),
    types.InlineKeyboardButton(">", callback_data="next_price_changes")
)
price_changes_markup.add(types.InlineKeyboardButton('« Назад', callback_data='price_back_to_period'))
