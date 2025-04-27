import telebot
from telebot import types
from inline_buttons_handler import handle_next_currency_button, handle_next_price_button, handle_previous_currency_button, handle_previous_price_button, handle_charts_back_to_coin, handle_price_back_to_period, handle_coin_back_to_menu
from markups.charts_markup import charts_markup
from commands_handler import commands_handler, start
from charts_buttons_handler import charts_buttons_handler
from period_changes_handler import period_changes_handler, chart_period_handler
import requests
from alerts_handler import show_alert_menu, start_add_alert, choose_coin, choose_direction, receive_threshold, choose_interval, list_alerts, start_remove_alert, confirm_remove_alert, back_to_menu, back_to_coin, back_to_threshold, back_to_direction
import notifications_handler
from markups.period_markup    import period_markup
from markups.price_changes_markup import price_changes_markup
from coins_handler       import coin_info_handler

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start_wrapper(call):
    start(call)
          
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

# Монети

# Inline-callback для «coininfo_<SYM>»
@bot.callback_query_handler(func=lambda c: c.data.startswith('coininfo_'))
def coininfo_wrapper(c):
    coin_info_handler(c)

# Alerts

# Обробка головного меню Alerts
@bot.callback_query_handler(func=lambda c: c.data == 'alert_add')
def add_alert_wrapper(c):
    start_add_alert(c)        # крок 1: показує "Choose coin for alert"

@bot.callback_query_handler(func=lambda c: c.data == 'alert_list')
def alert_list_wrapper(c):
    list_alerts(c)    # виводить список

@bot.callback_query_handler(func=lambda c: c.data == 'alert_remove')
def remove_alert_wrapper(c):
    start_remove_alert(c)

@bot.callback_query_handler(func=lambda c: c.data.startswith('alert_rm_'))
def confirm_remove_alert_wrapper(c):
    confirm_remove_alert(c)

# 3) Кроки створення нового alert  
#   a) вибір монети
@bot.callback_query_handler(func=lambda c: c.data.startswith('alert_coin_'))
def alert_coin_wrapper(c):
    choose_coin(c)

#   b) вибір напрямку (above/below)
@bot.callback_query_handler(func=lambda c: c.data.startswith('alert_dir_'))
def alert_direction_wrapper(c):
    choose_direction(c)

#   c) введення порогу (threshold) — обробляється через message_handler

@bot.message_handler(func=receive_threshold)
def threshold_wrapper(message):
    pass  # receive_threshold обробить

@bot.callback_query_handler(func=lambda c: c.data.startswith('alert_int_'))
def alert_interval_wrapper(c):
    choose_interval(c)

# Кнопки "Назад"

@bot.callback_query_handler(func=lambda c: c.data=='alert_back_to_menu')
def alert_back_menu_wrapper(c):
    back_to_menu(c)

@bot.callback_query_handler(func=lambda c: c.data=='alert_back_to_coin')
def alert_back_coin_wrapper(c):
    back_to_coin(c)

@bot.callback_query_handler(func=lambda c: c.data=='alert_back_to_threshold')
def alert_back_threshold_wrapper(c):
    back_to_threshold(c)

@bot.callback_query_handler(func=lambda c: c.data == 'alert_back_to_direction')
def alert_back_direction_wrapper(c):
    back_to_direction(c)

# Charts: назад до вибору монети
@bot.callback_query_handler(func=lambda c: c.data.startswith('charts_back_to_coin_'))
def charts_back_coin_wrapper(c):
    handle_charts_back_to_coin(c, bot, charts_markup)

# Price changes: назад до вибору періоду
@bot.callback_query_handler(func=lambda c: c.data == 'price_back_to_period')
def price_back_period_wrapper(c):
    handle_price_back_to_period(c, bot, period_markup)

# Монети: назад до вибору монети
@bot.callback_query_handler(func=lambda c: c.data == 'coin_back_to_menu')
def coin_back_menu_wrapper(c):
    handle_coin_back_to_menu(c)

@bot.message_handler(content_types='text')
def commands_wrapper(message):
    commands_handler(message)



bot.remove_webhook()

bot.polling(none_stop=True)
