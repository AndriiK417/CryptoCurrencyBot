import telebot
import requests
from markups.currency_markup import currency_markup
from markups.price_changes_markup import price_changes_markup
from period_changes_handler import current_period  # нова змінна
from commands_handler import skip_price, skip_currency
import period_changes_handler
from markups.charts_markup import charts_markup, get_chart_period_markup
from markups.period_markup import period_markup
from telebot import types
from markups.coins_markup import coins_markup
from notifications_handler import bot

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
    key = period_map.get(period_changes_handler.current_period, 'percent_change_24h')
    text = '\n'.join(
        f"{c['name']}: {round(float(c.get(key, 0)), 3)}% "
        for c in coins
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=price_changes_markup)

def handle_next_price_button(call):
    global skip_price
    skip_price += 10
    resp = requests.get(BASE_URL, params={'start': skip_price, 'limit': 10})
    coins = resp.json().get('data', [])
    key = period_map.get(period_changes_handler.current_period, 'percent_change_24h')
    text = '\n'.join(
        f"{c['name']}: {round(float(c.get(key, 0)), 3)}% "
        for c in coins
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=price_changes_markup)

def handle_charts_back_to_coin(call):
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    bot.send_message(
        call.message.chat.id,
        "Для якої монети показати графік?",
        reply_markup=charts_markup
    )

# Для Price Changes:
def handle_price_back_to_period(call, bot, period_markup):
    # того ж message, просто повернути клавіатуру price_changes_markup?
    bot.edit_message_text(
        "Виберіть період:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=period_markup
    )

@bot.callback_query_handler(func=lambda c: c.data == 'coin_back_to_menu')
def handle_coin_back_to_menu(call):
    # 1) Видаляємо поточне медіа-повідомлення
    bot.delete_message(call.message.chat.id, call.message.message_id)

    # 2) Надсилаємо нове текстове повідомлення з меню монет
    bot.send_message(
        call.message.chat.id,
        "Оберіть монету:",
        reply_markup=coins_markup
    )

