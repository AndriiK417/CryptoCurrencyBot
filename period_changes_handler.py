import telebot
import requests
from markups.price_changes_markup import price_changes_markup

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)

BASE_URL = 'https://api.coinlore.net/api/tickers/'

# поточний період
current_period = 'priceChange1h'

# мапа для ключів зміни ціни
period_map = {
    'priceChange1h':  'percent_change_1h',
    'priceChange1d':  'percent_change_24h',
    'priceChange1w':  'percent_change_7d',
}

def period_changes_handler(call):
    global current_period
    current_period = call.data  # наприклад, 'priceChange1d'
    resp = requests.get(BASE_URL, params={'start': 0, 'limit': 10})
    coins = resp.json().get('data', [])
    key = period_map.get(current_period, 'percent_change_24h')
    text = '\n'.join(
        f"{c['name']}: {round(float(c.get(key, 0)), 3)}% "
        for c in coins
    )

    bot.send_message(call.message.chat.id, text, reply_markup=price_changes_markup)
