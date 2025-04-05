from telebot import types

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = types.KeyboardButton('Currency')
button2 = types.KeyboardButton('Price changes')
button3 = types.KeyboardButton('Charts')

markup.add(button1, button2, button3)