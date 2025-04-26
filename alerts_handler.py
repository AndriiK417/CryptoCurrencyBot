from telebot import types
import notifications_handler
from notifications_handler import bot, user_jobs
from markups.alerts_markup import (
    alert_menu_markup,
    alert_coins_markup,
    alert_direction_markup,
    alert_threshold_markup,
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
    chat   = call.message.chat.id
    msg_id = call.message.message_id
    data   = call.data.split('_', 2)[2]  # 'above'|'below'|'pct'…
    state = user_state.setdefault(chat, {})

    # визначаємо режим
    if data in ('above', 'below'):
        state['mode'] = 'absolute'
        prompt = "3️⃣ Enter threshold price in USD (e.g. 70000):"
        callback_back = 'alert_back_to_direction'  # або 'alert_back_to_coin'
    else:
        # 'pct_up' або 'pct_down'
        direction = 'up' if data=='pct_up' else 'down'
        state['mode'] = 'percent'
        state['direction'] = direction
        prompt = "3️⃣ Enter threshold percent (e.g. 5 for 5%):"
        callback_back = 'alert_back_to_direction'

    state.update({
        'direction': data if state['mode']=='absolute' else state['direction'],
        'step':      'threshold',
        'message_id': msg_id
    })

    # клавіатура з однією кнопкою «Назад»
    back = types.InlineKeyboardMarkup()
    back.add(types.InlineKeyboardButton('« Назад', callback_data=callback_back))

    bot.edit_message_text(
        prompt,
        chat_id=chat,
        message_id=msg_id,
        reply_markup=back
    )


def receive_threshold(message):
    """Крок 4: отримання порогу та вибір інтервалу"""
    chat = message.chat.id
    state = user_state.get(chat, {})
    if state.get('step') != 'threshold':
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
        interval=state['interval'],
        mode=state['mode']
    )
    suffix = '%' if state.get('mode') == 'percent' else '$'
    bot.edit_message_text(
        "✅ Alert set:\n"
        f"{state['coin']} {state['direction']} {state['threshold']}{suffix}\n"
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
        back = types.InlineKeyboardMarkup()
        back.add(types.InlineKeyboardButton('« Назад', callback_data='alert_back_to_menu'))
        bot.edit_message_text(
            "У вас немає активних сповіщень.",
            chat_id=chat,
            message_id=msg_id,
            reply_markup=back
        )
        return
    lines = []
    for job_id in jobs:
        parts = job_id.split('_')
        # тепер parts = ['alert', chat, symbol, mode, direction, threshold, interval]
        if len(parts) >= 7:
            _, _, symbol, mode, direction, threshold, _ = parts[:7]
            suffix = '%' if mode == 'percent' else '$'
            lines.append(f"- {symbol} {direction} {threshold}{suffix}")
        else:
            lines.append(f"- {job_id}")
    text = "Ваші сповіщення:\n" + "\n".join(lines)
    back = types.InlineKeyboardMarkup()
    back.add(types.InlineKeyboardButton('« Назад', callback_data='alert_back_to_menu'))
    bot.edit_message_text(
        text,
        chat_id=chat,
        message_id=msg_id,
        reply_markup=back
    )


def start_remove_alert(call):
    """Крок 1: показати список сповіщень для видалення або повідомити, що їх немає."""
    chat = call.message.chat.id
    msg_id = call.message.message_id

    # дістаємо список сповіщень
    jobs = notifications_handler.user_jobs.get(chat, [])

    if not jobs:
        # Немає жодного сповіщення — редагуємо повідомлення з текстом і кнопкою Назад
        back = types.InlineKeyboardMarkup()
        back.add(types.InlineKeyboardButton('« Назад', callback_data='alert_back_to_menu'))

        bot.edit_message_text(
            "У вас немає активних сповіщень.",
            chat_id=chat,
            message_id=msg_id,
            reply_markup=back
        )
    else:
        # Є сповіщення — показуємо список на видалення
        markup = get_remove_alerts_markup(chat)
        bot.edit_message_text(
            "❌ Виберіть, яке сповіщення видалити:",
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

def back_to_menu(call):
    chat = call.message.chat.id
    msg_id = call.message.message_id
    user_state[chat]['step'] = 'menu'
    bot.edit_message_text(
        "🔔 Alerts menu:",
        chat_id=chat,
        message_id=msg_id,
        reply_markup=alert_menu_markup
    )

def back_to_coin(call):
    chat = call.message.chat.id
    msg_id = call.message.message_id
    user_state[chat]['step'] = 'coin'
    bot.edit_message_text(
        "1️⃣ Choose coin for alert:",
        chat_id=chat,
        message_id=msg_id,
        reply_markup=alert_coins_markup
    )

def back_to_threshold(call):
    chat = call.message.chat.id
    msg_id = call.message.message_id
    state  = user_state.get(chat, {})

    # Визначаємо, який саме prompt показати
    mode = state.get('mode', 'absolute')
    if mode == 'absolute':
        prompt = "3️⃣ Enter threshold price in USD (e.g. 70000):"
    else:  # percent
        prompt = "3️⃣ Enter threshold percent (e.g. 5 for 5%):"
    
    bot.edit_message_text(
        prompt,
        chat_id=chat,
        message_id=msg_id,
        reply_markup=alert_threshold_markup
    )

def back_to_direction(call):
    """Повернення до вибору direction (After coin selected)"""
    chat = call.message.chat.id
    msg_id = call.message.message_id
    # user_state[chat]['step'] = 'direction'
    state = user_state.get(chat)
    coin = state.get('coin', 'your coin')
    # Заново показати вибір direction
    bot.edit_message_text(
        f"2️⃣ {coin}: Above or Below?",
        chat_id=chat,
        message_id=msg_id,
        reply_markup=alert_direction_markup
    )
    # state['step'] = 'direction'

