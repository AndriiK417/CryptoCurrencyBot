import telebot
import requests
from markups.price_changes_markup import price_changes_markup

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)

period = 'priceChange1h'

def period_changes_handler(call):
    period = call.data
    PRICE_API_LINK = 'https://api.coinstats.app/public/v1/coins?skip=0&limit=10&currency=USD'

    response = requests.get(PRICE_API_LINK).json()['coins']
    response_message = ''

    for i in range(10):
        response_message += response[i]['name'] + ': ' + str(round(response[i][period], 3)) + '% \n'
                
    bot.send_message(call.message.chat.id, response_message, reply_markup=price_changes_markup)