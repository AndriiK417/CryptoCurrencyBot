import telebot
from telebot import types
from inline_buttons_handler import handle_next_currency_button, handle_next_price_button, handle_previous_currency_button, handle_previous_price_button
from commands_handler import commands_handler
from charts_buttons_handler import charts_buttons_handler
from markups.markup import markup
from period_changes_handler import period_changes_handler, chart_period_handler
import requests
from alerts_handler import show_alert_menu, start_add_alert, choose_coin, choose_direction, receive_threshold, choose_interval, list_alerts, start_remove_alert, confirm_remove_alert
from markups.alerts_markup import (
    alert_menu_markup,
    alert_coins_markup,
    alert_direction_markup,
    alert_interval_markup,
    get_remove_alerts_markup
)
import notifications_handler

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hi, {0.first_name}'.format(message.from_user), reply_markup=markup)

# 1) Кнопка в основному меню "Alerts"
@bot.message_handler(func=lambda m: m.text == 'Alerts')
def cb_show_alert_menu(message):
    show_alert_menu(message)  # надсилає alert_menu_markup

# 2) Обробка головного меню Alerts
@bot.callback_query_handler(func=lambda c: c.data == 'alert_add')
def cb_alert_add(c):
    start_add_alert(c)        # крок 1: показує "Choose coin for alert"

@bot.callback_query_handler(func=lambda c: c.data == 'alert_list')
def cb_alert_list(c):
    list_alerts(c.message)    # виводить список

@bot.callback_query_handler(func=lambda c: c.data == 'alert_remove')
def cb_alert_remove(c):
    chat = c.message.chat.id
    markup = get_remove_alerts_markup(chat)
    if not markup.keyboard:
        bot.send_message(chat, "У вас немає активних сповіщень.")
    else:
        bot.send_message(chat, "❌ Виберіть сповіщення для видалення:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith('alert_rm_'))
def cb_alert_rm(c):
    confirm_remove_alert(c)

# 3) Кроки створення нового alert  
#   a) вибір монети
@bot.callback_query_handler(func=lambda c: c.data.startswith('alert_coin_'))
def cb_alert_coin(c):
    choose_coin(c)

#   b) вибір напрямку (above/below)
@bot.callback_query_handler(func=lambda c: c.data.startswith('alert_dir_'))
def cb_alert_dir(c):
    choose_direction(c)

#   c) введення порогу (threshold) — обробляється через message_handler

@bot.message_handler(func=receive_threshold)
def mh_threshold(message):
    pass  # receive_threshold обробить

@bot.callback_query_handler(func=lambda c: c.data.startswith('alert_int_'))
def cb_alert_int(c): choose_interval(c)

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

# 1) Обробник вибору монети для графіка
@bot.callback_query_handler(func=lambda call: call.data.startswith('selectchart_'))
def charts_buttons_wrapper(call):
    charts_buttons_handler(call)

# 2) Обробник вибору періоду та відправки графіка
@bot.callback_query_handler(func=lambda call: call.data.startswith('chart_'))
def chart_period_wrapper(call):
    chart_period_handler(call)



bot.remove_webhook()

bot.polling(none_stop=True)
