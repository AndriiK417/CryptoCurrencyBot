import telebot
import requests
from markups.charts_markup import charts_markup
from markups.currency_markup import currency_markup
from markups.price_changes_markup import price_changes_markup
from markups.period_markup import period_markup

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)

CURRENCY_API_LINK = 'https://api.coinstats.app/public/v1/coins?skip=0&limit=10&currency=USD'

skip_price = 0
skip_currency = 0

def commands_handler(message):
    global skip_currency
    global skip_price

    skip_currency = 0
    skip_price = 0

    if message.chat.type == 'private':
        if message.text == 'Currency':
            response = requests.get(CURRENCY_API_LINK).json()['coins']
            response_message = ''

            for i in range(10):
                response_message += response[i]['name'] + ' - ' + str(round(response[i]['price'], 3)) + '$ \n'
                
            bot.send_message(message.chat.id, response_message, reply_markup=currency_markup)

        elif message.text == 'Price changes':
            bot.send_message(message.chat.id, "Choose period:", reply_markup=period_markup)

        elif message.text == 'Charts':
            bot.send_message(message.chat.id, "Choose the crypto-chart you need:", reply_markup=charts_markup)
