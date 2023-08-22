import telebot
import requests

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)


def charts_buttons_handler(call):
    coin = call.data
    CHARTS_API_LINK = f'https://api.chart-img.com/v1/tradingview/mini-chart?key=qJX6lruQMB9Yhkj7ub87z3vrFa8z6hI13AgoaLdS&symbol=BINANCE:{coin}&width=600&height=400&interval=3M&theme=light'

    response = requests.get(CHARTS_API_LINK)
    bot.send_photo(call.message.chat.id, response.content)
    bot.send_message(call.message.chat.id, "Here's your chart")
