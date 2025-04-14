# alerts_handler.py

import notifications_handler
from notifications_handler import bot
from markups.alerts_markup import (
    alert_menu_markup,
    alert_coins_markup,
    alert_direction_markup,
    alert_interval_markup,
    get_remove_alerts_markup
)

# Стан користувачів: chat_id → { step, coin, direction, threshold, interval }
user_state = {}

def show_alert_menu(message):
    """Показує головне меню Alerts: Add / List / Remove"""
    bot.send_message(
        message.chat.id,
        "🔔 Alerts menu:",
        reply_markup=alert_menu_markup
    )

def start_add_alert(call):
    """Крок 1: вибір монети"""
    chat = call.message.chat.id
    user_state[chat] = {'step': 'coin'}
    bot.send_message(
        chat,
        "1️⃣ Choose coin for alert:",
        reply_markup=alert_coins_markup
    )

def choose_coin(call):
    """Крок 2: вибір напрямку (above/below)"""
    chat = call.message.chat.id
    sym = call.data.split('_', 2)[2]  # 'alert_coin_BTCUSD'
    user_state[chat]['coin'] = sym
    user_state[chat]['step'] = 'direction'
    bot.send_message(
        chat,
        f"2️⃣ {sym}: Above or Below?",
        reply_markup=alert_direction_markup
    )

def choose_direction(call):
    """Крок 3: введення порогу"""
    chat = call.message.chat.id
    direction = call.data.split('_')[2]  # 'above' або 'below'
    user_state[chat]['direction'] = direction
    user_state[chat]['step'] = 'threshold'
    bot.send_message(
        chat,
        "3️⃣ Enter threshold price in USD (e.g. 70000):"
    )

def receive_threshold(message):
    """Крок 4: вибір інтервалу після введення порогу"""
    chat = message.chat.id
    state = user_state.get(chat)
    if not state or state.get('step') != 'threshold':
        return False  # не наш випадок
    try:
        th = float(message.text)
    except ValueError:
        bot.send_message(chat, "❗ Please enter a valid number.")
        return True  # оброблено
    state['threshold'] = th
    state['step'] = 'interval'
    bot.send_message(
        chat,
        "4️⃣ Choose check interval:",
        reply_markup=alert_interval_markup
    )
    return True

def choose_interval(call):
    """Крок 5: створення job-а"""
    chat = call.message.chat.id
    state = user_state.get(chat, {})
    interval = call.data.split('_')[2]  # 'hourly' або 'daily'
    state['interval'] = interval

    notifications_handler.schedule_alert(
        chat_id   = chat,
        symbol    = state['coin'],
        direction = state['direction'],
        threshold = state['threshold'],
        interval  = state['interval']
    )
    bot.send_message(
        chat,
        "✅ Alert set:\n"
        f"{state['coin']} {state['direction']} {state['threshold']}$\n"
        f"every {state['interval']}"
    )
    user_state.pop(chat, None)

def list_alerts(message):
    """Виводить список alert-ів"""
    # Передаємо message одразу в notifications_handler
    notifications_handler.list_alerts(message)

def start_remove_alert(call):
    """Крок 1: показати список сповіщень для видалення"""
    chat = call.message.chat.id
    markup = get_remove_alerts_markup(chat)
    if not markup.keyboard:
        bot.send_message(chat, "У вас немає активних сповіщень.")
    else:
        bot.send_message(
            chat,
            "❌ Виберіть сповіщення, яке хочете видалити:",
            reply_markup=markup
        )

def confirm_remove_alert(call):
    """Крок 2: обробити натискання і видалити alert"""
    chat = call.message.chat.id
    job_id = call.data[len('alert_rm_'):]
    notifications_handler.cancel_alert(chat, job_id)
