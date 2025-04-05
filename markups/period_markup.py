from telebot import types

period_markup = types.InlineKeyboardMarkup()
variant1 = types.InlineKeyboardButton('1 hour', callback_data='priceChange1h')
variant2 = types.InlineKeyboardButton('1 day', callback_data='priceChange1d')
variant3 = types.InlineKeyboardButton('1 week', callback_data='priceChange1w') 

period_markup.add(variant1, variant2, variant3)