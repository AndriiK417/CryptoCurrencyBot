from telebot import types
import notifications_handler
from notifications_handler import bot, scheduler, user_jobs
from markups.alerts_markup import (
    alert_menu_markup,
    alert_coins_markup,
    alert_type_markup,
    alert_direction_price_markup,
    alert_direction_percent_markup,
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


def choose_coin(call: types.CallbackQuery):
    """2️⃣ Після вибору монети — вибір метрики: price або percent"""
    chat   = call.message.chat.id
    msg_id = call.message.message_id
    symbol = call.data.split('_',2)[2]  # alert_coin_BTCUSD → BTCUSD

    st = user_state[chat]
    st.update({'coin': symbol, 'step': 'type'})

    bot.edit_message_text(
        f"2️⃣ {symbol}: Choose alert type",
        chat_id=chat,
        message_id=msg_id,
        reply_markup=alert_type_markup
    )


def choose_type(call: types.CallbackQuery):
    """3️⃣ Вибір метрики → price чи percent, потім direction"""
    chat   = call.message.chat.id
    msg_id = call.message.message_id
    mode   = call.data.split('_',2)[2]  # 'price' або 'percent'

    st = user_state[chat]
    st.update({'mode': mode, 'step': 'direction'})

    # вибираємо потрібний markup
    if mode == 'price':
        direction_markup = alert_direction_price_markup
        title = "Price alert: Above or Below $?"
    else:
        direction_markup = alert_direction_percent_markup
        title = "Percent alert: ▲ or ▼ %?"

    # Змінюємо текст і клавіатуру на direction-menu
    bot.edit_message_text(
        f"3️⃣ {title}",
        chat_id=chat,
        message_id=msg_id,
        reply_markup=direction_markup
    )


def choose_direction(call):
    chat   = call.message.chat.id
    msg_id = call.message.message_id
    direction = call.data.split('_',2)[2]  # 'above' чи 'below'

    state = user_state[chat]
    state.update({'direction': direction, 'step': 'threshold'})

    # Виводимо prompt для threshold
    prompt = ("4️⃣ Enter threshold price in USD (e.g. 70000):"
              if state['mode']=='price'
              else "4️⃣ Enter threshold percent (e.g. 5 for 5%):")

    # клавіатура з однією кнопкою «Назад»
    back = types.InlineKeyboardMarkup()
    back.add(types.InlineKeyboardButton('« Назад', callback_data='alert_back_to_direction'))

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
        f"{state['interval']}",
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


def confirm_remove_alert(call: types.CallbackQuery):
    """
    Отримує job_id із callback_data = 'alert_rm_<job_id>',
    одразу видаляє його зі scheduler і з user_jobs,
    формує дружнє повідомлення та редагує/відправляє його.
    """
    chat = call.message.chat.id
    msg_id = call.message.message_id

    # дістаємо чистий job_id
    job_id = call.data[len('alert_rm_'):]

    # спарсимо дружній лейбл зі job_id (suffix % або $)
    parts = job_id.split('_')
    label = job_id
    if len(parts) >= 7:
        _, _, symbol, mode, direction, threshold, _ = parts[:7]
        suffix = '%' if mode == 'percent' else '$'
        label = f"{symbol} {direction} {threshold}{suffix}"

    try:
        # 1) видалити job із scheduler-а
        scheduler.remove_job(job_id)
        # 2) видалити job_id з user_jobs
        if job_id in user_jobs.get(chat, []):
            user_jobs[chat].remove(job_id)

        # 3) підтвердження юзеру – редагуємо те саме повідомлення
        bot.edit_message_text(
            f"🗑️ Alert removed: {label}",
            chat_id=chat,
            message_id=msg_id,
            reply_markup=None
        )

    except Exception as e:
        # якщо щось не так — повідомимо про помилку й залишимо кнопки
        bot.edit_message_text(
            f"⚠️ Не вдалося видалити сповіщення:\n{e}",
            chat_id=chat,
            message_id=msg_id,
            reply_markup=get_remove_alerts_markup(chat)
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

def back_to_type(call):
    """
    Повернення на крок вибору метрики (price або percent)
    """
    chat   = call.message.chat.id
    msg_id = call.message.message_id
    state  = user_state.get(chat, {})

    # Якщо монету вже вибрали — дістаємо її для заголовка
    coin = state.get('coin', 'your coin')

    # Редагуємо те саме повідомлення
    bot.edit_message_text(
        f"2️⃣ {coin}: Choose alert type",
        chat_id=chat,
        message_id=msg_id,
        reply_markup=alert_type_markup
    )

    # Оновлюємо FSM-стан
    state['step'] = 'type'

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
    """
    Повернення на крок вибору напрямку:
    – якщо mode=='price' → клавіатура з “🔼 Above $”/“🔽 Below $”
    – якщо mode=='percent' → клавіатура з “📈 ▲ %”/“📉 ▼ %”
    """
    chat   = call.message.chat.id
    msg_id = call.message.message_id
    state  = user_state.get(chat, {})

    # Дістаємо поточний режим ('price' або 'percent')
    mode = state.get('mode', 'price')
    coin = state.get('coin', 'your coin')

    if mode == 'price':
        direction_markup    = alert_direction_price_markup
        title     = f"3️⃣ {coin}: Price alert – Above or Below $?"
    else:
        direction_markup    = alert_direction_percent_markup
        title     = f"3️⃣ {coin}: Percent alert – ▲ or ▼ %?"

    # Редагуємо повідомлення з відповідними кнопками
    bot.edit_message_text(
        title,
        chat_id=chat,
        message_id=msg_id,
        reply_markup=direction_markup
    )
    # state['step'] = 'direction'

