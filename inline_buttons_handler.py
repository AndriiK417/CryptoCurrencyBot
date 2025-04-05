import telebot
import requests
from markups.currency_markup import currency_markup
from markups.price_changes_markup import price_changes_markup
from period_changes_handler import current_period  # нова змінна
from commands_handler import skip_price, skip_currency

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)

BASE_URL = 'https://api.coinlore.net/api/tickers/'

# мапа для ключів зміни ціни
period_map = {
    'priceChange1h':  'percent_change_1h',
    'priceChange1d':  'percent_change_24h',
    'priceChange1w':  'percent_change_7d',
}

def handle_previous_currency_button(call):
    global skip_currency
    if skip_currency >= 10:
        skip_currency -= 10
    resp = requests.get(BASE_URL, params={'start': skip_currency, 'limit': 10})
    coins = resp.json().get('data', [])
    text = '\n'.join(
        f"{c['name']} — {round(float(c['price_usd']), 3)}$"
        for c in coins
    )

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=currency_markup)

def handle_next_currency_button(call):
    global skip_currency
    skip_currency += 10
    resp = requests.get(BASE_URL, params={'start': skip_currency, 'limit': 10})
    coins = resp.json().get('data', [])
    text = '\n'.join(
        f"{c['name']} — {round(float(c['price_usd']), 3)}$"
        for c in coins
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=currency_markup)

def handle_previous_price_button(call):
    global skip_price
    if skip_price >= 10:
        skip_price -= 10
    resp = requests.get(BASE_URL, params={'start': skip_price, 'limit': 10})
    coins = resp.json().get('data', [])
    key = period_map.get(current_period, 'percent_change_24h')
    text = '\n'.join(
        f"{c['name']} — {round(float(c['price_usd']), 3)}$"
        for c in coins
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=price_changes_markup)

def handle_next_price_button(call):
    global skip_price
    skip_price += 10
    resp = requests.get(BASE_URL, params={'start': skip_price, 'limit': 10})
    coins = resp.json().get('data', [])
    key = period_map.get(current_period, 'percent_change_24h')
    text = '\n'.join(
        f"{c['name']} — {round(float(c['price_usd']), 3)}$"
        for c in coins
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=price_changes_markup)
