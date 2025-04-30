from telebot import types

period_markup = types.InlineKeyboardMarkup()
variant1 = types.InlineKeyboardButton('1 година', callback_data='priceChange1h')
variant2 = types.InlineKeyboardButton('1 день', callback_data='priceChange1d')
variant3 = types.InlineKeyboardButton('1 тиждень', callback_data='priceChange1w') 

period_markup.add(variant1, variant2, variant3)
