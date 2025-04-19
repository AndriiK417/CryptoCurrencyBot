import notifications_handler
from notifications_handler import bot, user_jobs
from markups.alerts_markup import (
    alert_menu_markup,
    alert_coins_markup,
    alert_direction_markup,
    alert_interval_markup,
    get_remove_alerts_markup
)

# Стан користувачів: chat_id → { step, coin, direction, threshold, interval, message_id }
user_state = {}


def show_alert_menu(message):
    """
    Показує головне меню Alerts: Add / List / Remove
    """
    sent = bot.send_message(
        message.chat.id,
        "🔔 Alerts menu:",
        reply_markup=alert_menu_markup
    )
    # Зберігаємо message_id, щоб можна було редагувати
    user_state[message.chat.id] = {'message_id': sent.message_id}


def start_add_alert(call):
    """Крок 1: вибір монети — редагуємо повідомлення"""
    chat = call.message.chat.id
    msg_id = call.message.message_id
    user_state[chat].update({'step': 'coin', 'message_id': msg_id})
    bot.edit_message_text(
        "1️⃣ Choose coin for alert:",
        chat_id=chat,
        message_id=msg_id,
        reply_markup=alert_coins_markup
    )


def choose_coin(call):
    """Крок 2: вибір напрямку"""
    chat = call.message.chat.id
    msg_id = call.message.message_id
    sym = call.data.split('_', 2)[2]
    state = user_state.get(chat, {})
    state.update({'coin': sym, 'step': 'direction', 'message_id': msg_id})
    bot.edit_message_text(
        f"2️⃣ {sym}: Above or Below?",
        chat_id=chat,
        message_id=msg_id,
        reply_markup=alert_direction_markup
    )


def choose_direction(call):
    """Крок 3: введення порогу"""
    chat = call.message.chat.id
    msg_id = call.message.message_id
    direction = call.data.split('_')[2]
    state = user_state.get(chat, {})
    state.update({'direction': direction, 'step': 'threshold', 'message_id': msg_id})
    bot.edit_message_text(
        "3️⃣ Enter threshold price in USD (e.g. 70000):",
        chat_id=chat,
        message_id=msg_id,
        reply_markup=None
    )


def receive_threshold(message):
    """Крок 4: отримання порогу та вибір інтервалу"""
    chat = message.chat.id
    state = user_state.get(chat)
    if not state or state.get('step') != 'threshold':
        return False
    try:
        th = float(message.text)
    except ValueError:
        bot.send_message(chat, "❗ Please enter a valid number.")
        return True
    # видаляємо повідомлення користувача з порогом
    bot.delete_message(chat_id=chat, message_id=message.message_id)
    state.update({'threshold': th, 'step': 'interval'})
    msg_id = state.get('message_id')
    bot.edit_message_text(
        "4️⃣ Choose check interval:",
        chat_id=chat,
        message_id=msg_id,
        reply_markup=alert_interval_markup
    )
    return True


def choose_interval(call):
    """Крок 5: створення alert та підтвердження"""
    chat = call.message.chat.id
    msg_id = call.message.message_id
    state = user_state.get(chat, {})
    interval = call.data.split('_', 2)[2]
    state['interval'] = interval

    notifications_handler.schedule_alert(
        chat_id=chat,
        symbol=state['coin'],
        direction=state['direction'],
        threshold=state['threshold'],
        interval=state['interval']
    )
    bot.edit_message_text(
        "✅ Alert set:\n"
        f"{state['coin']} {state['direction']} {state['threshold']}$\n"
        f"every {state['interval']}",
        chat_id=chat,
        message_id=msg_id,
        reply_markup=None
    )
    user_state.pop(chat, None)


def list_alerts(call):
    """Відображення списку alert-ів у тому ж повідомленні"""
    chat = call.message.chat.id
    msg_id = call.message.message_id
    jobs = user_jobs.get(chat, [])
    if not jobs:
        bot.edit_message_text(
            "У вас немає активних сповіщень.",
            chat_id=chat,
            message_id=msg_id,
            reply_markup=None
        )
        return
    lines = []
    for job_id in jobs:
        parts = job_id.split('_', 5)
        if len(parts) == 6:
            _, _, symbol, direction, threshold, _ = parts
            lines.append(f"- {symbol} {direction} {threshold}$")
        else:
            lines.append(f"- {job_id}")
    text = "Ваші сповіщення:\n" + "\n".join(lines)
    bot.edit_message_text(
        text,
        chat_id=chat,
        message_id=msg_id,
        reply_markup=None
    )


def start_remove_alert(call):
    """Крок 1: показати меню видалення у тому ж повідомленні"""
    chat = call.message.chat.id
    msg_id = call.message.message_id
    markup = get_remove_alerts_markup(chat)
    if not markup.keyboard:
        bot.edit_message_text(
            "У вас немає активних сповіщень.",
            chat_id=chat,
            message_id=msg_id,
            reply_markup=None
        )
    else:
        bot.edit_message_text(
            "❌ Виберіть сповіщення для видалення:",
            chat_id=chat,
            message_id=msg_id,
            reply_markup=markup
        )


def confirm_remove_alert(call):
    """Крок 2: видалення alert і очищення кнопок"""
    chat = call.message.chat.id
    msg_id = call.message.message_id
    job_id = call.data.split('alert_rm_')[1]
    notifications_handler.cancel_alert(chat_id=chat, job_id=job_id)
    bot.edit_message_reply_markup(
        chat_id=chat,
        message_id=msg_id,
        reply_markup=None
    )
