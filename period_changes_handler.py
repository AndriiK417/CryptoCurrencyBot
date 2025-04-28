import telebot
import requests
from telebot.types import InputMediaPhoto
from notifications_handler import bot
from markups.charts_markup import get_chart_period_markup
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
    chat_id    = call.message.chat.id
    message_id = call.message.message_id
    # форматуємо: 'chart_BTCUSD_1D'
    _, coin, interval = call.data.split('_', 2)

    # Робимо запит до Chart-Img
    CHARTS_API_LINK = (
        f'https://api.chart-img.com/v1/tradingview/mini-chart'
        f'?key=qJX6lruQMB9Yhkj7ub87z3vrFa8z6hI13AgoaLdS'
        f'&symbol=BINANCE:{coin}'
        f'&interval={interval}'
        f'&width=600&height=400'
        f'&theme=light'
    )
    resp = requests.get(CHARTS_API_LINK)
    if resp.status_code != 200:
        bot.answer_callback_query(call.id, "Не вдалося завантажити графік.")
        return

    # Створюємо media із контенту та редагуємо повідомлення
    media = InputMediaPhoto(media=resp.content)
    bot.edit_message_media(
        media=media,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=get_chart_period_markup(coin)  # клавіатура з 1D,1M,3M,1Y + «Назад»
    )
