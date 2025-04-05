import telebot
import requests
from markups.currency_markup import currency_markup
from markups.price_changes_markup import price_changes_markup
from period_changes_handler import period
from commands_handler import skip_price, skip_currency

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)

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
        response_message += response[i]['name'] + ": " + str(response[i][period]) + '% \n'

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=response_message, reply_markup=price_changes_markup)

def handle_next_price_button(call):
    global skip_price

    if skip_price < 60:
        skip_price += 10 

    API_LINK = f'https://api.coinstats.app/public/v1/coins?skip={skip_price}&limit=10&currency=USD'

    response = requests.get(API_LINK).json()['coins']
    response_message = ''

    for i in range(10):
        response_message += response[i]['name'] + ": " + str(response[i][period]) + '% \n'

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=response_message, reply_markup=price_changes_markup)
