from telebot import types

alert_menu_markup = types.InlineKeyboardMarkup(row_width=2)
alert_menu_markup.add(
    types.InlineKeyboardButton('➕ Add Alert', callback_data='alert_add'),
    types.InlineKeyboardButton('📋 List Alerts', callback_data='alert_list'),
)
