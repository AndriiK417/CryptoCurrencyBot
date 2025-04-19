import telebot
from markups.charts_markup import charts_markup, get_chart_period_markup

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)

def charts_buttons_handler(call):
    # call.data — наприклад, 'selectchart_BTCUSD'
    # видаляємо префікс, щоб отримати символ
    _, coin = call.data.split('_', 1)
    bot.send_message(
        call.message.chat.id,
        f"Оберіть період для графіка {coin}:",
        reply_markup=get_chart_period_markup(coin)
    )
