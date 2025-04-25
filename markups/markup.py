from telebot import types

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
button0 = types.KeyboardButton('Монети')
button1 = types.KeyboardButton('Currency')
button2 = types.KeyboardButton('Price changes')
button3 = types.KeyboardButton('Charts')
button4 = types.KeyboardButton('Alerts')

markup.add(button0, button1, button2, button3, button4)
