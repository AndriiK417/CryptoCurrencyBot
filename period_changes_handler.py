import telebot
import requests
from notifications_handler import bot
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
    """
    Замість send_message — редагуємо вихідне "Choose period" повідомлення
    на список змін цін + пагінацію.
    """
    chat_id    = call.message.chat.id
    message_id = call.message.message_id
    period = call.data  # наприклад 'priceChange1d'

    resp = requests.get(BASE_URL, params={'start': 0, 'limit': 10})
    coins = resp.json().get('data', [])
    key = period_map.get(period, 'percent_change_24h')
    text = '\n'.join(
        f"{c['name']}: {round(float(c.get(key, 0)), 3)}% "
        for c in coins
    )

    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=price_changes_markup
    )


def chart_period_handler(call):
    # call.data: 'chart_<COIN>_<INTERVAL>'
    _, coin, interval = call.data.split('_', 2)
    CHARTS_API_LINK = (
        f'https://api.chart-img.com/v1/tradingview/mini-chart'
        f'?key=qJX6lruQMB9Yhkj7ub87z3vrFa8z6hI13AgoaLdS'
        f'&symbol=BINANCE:{coin}'
        f'&width=600&height=400'
        f'&interval={interval}'
        f'&theme=light'
    )
    resp = requests.get(CHARTS_API_LINK)
    if resp.status_code == 200:
        bot.send_photo(call.message.chat.id, resp.content)
    else:
        bot.send_message(call.message.chat.id, "Не вдалося завантажити графік. Спробуйте пізніше.")

