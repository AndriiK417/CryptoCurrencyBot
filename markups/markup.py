from telebot import types

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
button0 = types.KeyboardButton('Монети')
button1 = types.KeyboardButton('Ціни')
button2 = types.KeyboardButton('Зміни цін')
button3 = types.KeyboardButton('Графіки')
button4 = types.KeyboardButton('Сповіщення')

markup.add(button0, button1, button2, button3, button4)
