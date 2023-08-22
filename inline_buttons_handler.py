import telebot
import requests
from telebot import types

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)

skip_currency = 0
skip_price = 0

currency_markup = types.InlineKeyboardMarkup()
currency_markup.row_width = 2
currency_markup.add(types.InlineKeyboardButton("<", callback_data="previous_currency"),
types.InlineKeyboardButton(">", callback_data="next_currency"))

price_changes_markup = types.InlineKeyboardMarkup()
price_changes_markup.row_width = 2
price_changes_markup.add(types.InlineKeyboardButton("<", callback_data="previous_price_changes"),
types.InlineKeyboardButton(">", callback_data="next_price_changes"))

charts_markup = types.InlineKeyboardMarkup()
charts_markup.row_width = 6
charts_markup.add(types.InlineKeyboardButton("Choose the other chart", callback_data="chart"))

def handle_previous_currency_button(call):
    global skip_currency

    if skip_currency > 0:
        skip_currency -= 10 

    API_LINK = f'https://api.coinstats.app/public/v1/coins?skip={skip_currency}&limit=10&currency=USD'

    response = requests.get(API_LINK).json()['coins']
    response_message = ''

    for i in range(10):
        response_message += response[i]['name'] + ' - ' + str(round(response[i]['price'], 3)) + '$ \n'

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=response_message, reply_markup=currency_markup)

def handle_next_currency_button(call):
    global skip_currency

    if skip_currency < 60:
        skip_currency += 10 

    API_LINK = f'https://api.coinstats.app/public/v1/coins?skip={skip_currency}&limit=10&currency=USD'

    response = requests.get(API_LINK).json()['coins']
    response_message = ''

    for i in range(10):
        response_message += response[i]['name'] + ' - ' + str(round(response[i]['price'], 3)) + '$ \n'

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=response_message, reply_markup=currency_markup)

def handle_previous_price_button(call):
    global skip_price

    if skip_price > 0:
        skip_price -= 10 

    API_LINK = f'https://api.coinstats.app/public/v1/coins?skip={skip_price}&limit=10&currency=USD'

    response = requests.get(API_LINK).json()['coins']
    response_message = ''

    for i in range(10):
        response_message += response[i]['name'] + ": " + str(response[i]['priceChange1w']) + '% \n'

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=response_message, reply_markup=price_changes_markup)

def handle_next_price_button(call):
    global skip_price

    if skip_price < 60:
        skip_price += 10 

    API_LINK = f'https://api.coinstats.app/public/v1/coins?skip={skip_price}&limit=10&currency=USD'

    response = requests.get(API_LINK).json()['coins']
    response_message = ''

    for i in range(10):
        response_message += response[i]['name'] + ": " + str(response[i]['priceChange1w']) + '% \n'

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=response_message, reply_markup=price_changes_markup)
