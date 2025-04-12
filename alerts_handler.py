import notifications_handler
from notifications_handler import bot
from markups.alert_menu_markup      import alert_menu_markup
from markups.alert_coins_markup     import alert_coins_markup
from markups.alert_direction_markup import alert_direction_markup
from markups.alert_interval_markup  import alert_interval_markup

# Стан користувачів: chat_id → { step, coin, direction, threshold, interval }
user_state = {}

def show_alert_menu(message):
    """
    Показує головне меню Alerts: Add / List
    """
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
    sym = call.data.split('_', 2)[2]  # з 'alert_coin_BTCUSD' отримаємо 'BTCUSD'
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
        return False  # не наш випадок, пропускаємо
    try:
        th = float(message.text)
    except ValueError:
        bot.send_message(chat, "❗ Please enter a valid number.")
        return True  # обробили це повідомлення
    state['threshold'] = th
    state['step'] = 'interval'
    bot.send_message(
        chat,
        "4️⃣ Choose check interval:",
        reply_markup=alert_interval_markup
    )
    return True  # повідомлення оброблено

def choose_interval(call):
    """Крок 5: створення job-а"""
    chat = call.message.chat.id
    state = user_state.get(chat, {})
    interval = call.data.split('_')[2]  # 'hourly' або 'daily'
    state['interval'] = interval

    job_id = notifications_handler.schedule_alert(
        chat_id   = chat,
        symbol    = state['coin'],
        direction = state['direction'],
        threshold = state['threshold'],
        interval  = state['interval']
    )
    bot.send_message(
        chat,
        f"✅ Alert set:\n"
        f"{state['coin']} {state['direction']} {state['threshold']}$\n"
        f"every {state['interval']}\n"
        f"(job_id: {job_id})"
    )
    user_state.pop(chat, None)

def list_alerts(call):
    """Відобразити список alert-ів"""
    notifications_handler.list_alerts(call.message)

def remove_alert(call):
    """Видалити alert за job_id"""
    notifications_handler.remove_alert(call.message)
