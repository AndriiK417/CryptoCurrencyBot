import telebot
from telebot import types
from inline_buttons_handler import handle_next_currency_button, handle_next_price_button, handle_previous_currency_button, handle_previous_price_button
from commands_handler import commands_handler
from charts_buttons_handler import charts_buttons_handler
from markups.markup import markup
from period_changes_handler import period_changes_handler

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hi, {0.first_name}'.format(message.from_user), reply_markup=markup)

@bot.message_handler(content_types='text')
def commands_wrapper(message):
    commands_handler(message)
            
@bot.callback_query_handler(func=lambda call: call.data.startswith('previous_currency'))
def previous_currency_wrapper(call):
    handle_previous_currency_button(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('next_currency'))
def next_currency_wrapper(call):
    handle_next_currency_button(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('previous_price_changes'))
def previous_pice_wrapper(calc):
    handle_previous_price_button(calc)

@bot.callback_query_handler(func=lambda call: call.data.startswith('next_price_changes'))
def next_price_wrapper(calc):
    handle_next_price_button(calc)

@bot.callback_query_handler(func=lambda call: call.data.startswith('priceChange'))
def period_changes_wrapper(call):
    period_changes_handler(call)

@bot.callback_query_handler(func=lambda call: True)
def charts_buttons_wrapper(call):
    charts_buttons_handler(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('chart_'))
def chart_period_handler(call):
    # call.data виглядає як 'chart_BTCUSD_1h'
    _, coin, period = call.data.split('_')
    # period — '1h' або '1d' або '1w'
    CHARTS_API_LINK = (
        f'https://api.chart-img.com/v1/tradingview/mini-chart'
        f'?key=qJX6lruQMB9Yhkj7ub87z3vrFa8z6hI13AgoaLdS'
        f'&symbol=BINANCE:{coin}'
        f'&width=600&height=400'
        f'&interval={period}'
        f'&theme=light'
    )
    resp = requests.get(CHARTS_API_LINK)
    if resp.status_code == 200:
        bot.send_photo(call.message.chat.id, resp.content)
    else:
        bot.send_message(call.message.chat.id, "Не вдалося завантажити графік. Спробуйте пізніше.")

bot.polling(none_stop=True)
