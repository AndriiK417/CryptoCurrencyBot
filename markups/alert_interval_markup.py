from telebot import types

alert_interval_markup = types.InlineKeyboardMarkup(row_width=2)
alert_interval_markup.add(
    types.InlineKeyboardButton('🕒 Hourly', callback_data='alert_int_hourly'),
    types.InlineKeyboardButton('📅 Daily',  callback_data='alert_int_daily'),
)
