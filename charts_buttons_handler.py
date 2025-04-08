import telebot
from markups.chart_period_markup import get_chart_period_markup

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)

def charts_buttons_handler(call):
    # call.data — це, наприклад, 'BTCUSD'
    coin = call.data
    # просимо обрати період
    bot.send_message(
        call.message.chat.id,
        f"Оберіть період для графіка {coin}:",
        reply_markup=get_chart_period_markup(coin)
    )
