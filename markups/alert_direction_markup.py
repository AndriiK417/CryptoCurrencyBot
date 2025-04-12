from telebot import types

alert_direction_markup = types.InlineKeyboardMarkup(row_width=2)
alert_direction_markup.add(
    types.InlineKeyboardButton('🔼 Above', callback_data='alert_dir_above'),
    types.InlineKeyboardButton('🔽 Below', callback_data='alert_dir_below'),
)
