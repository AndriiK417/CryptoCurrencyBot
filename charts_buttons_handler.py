import telebot
import requests
from telebot import types
from notifications_handler import bot
from markups.charts_markup import charts_markup, get_chart_period_markup

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)

def charts_buttons_handler(call: types.CallbackQuery):
    """
    Замість send_message — редагуємо те ж саме повідомлення:
    від "Choose coin" → "Choose period"
    """
    chat_id    = call.message.chat.id
    message_id = call.message.message_id
    _, coin = call.data.split('_', 1)  # 'selectchart_BTCUSD' → coin='BTCUSD'

    bot.edit_message_text(
        text=f"Оберіть період для графіка {coin}:",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=get_chart_period_markup(coin)
    )

