import telebot
import requests
from apscheduler.schedulers.background import BackgroundScheduler

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)

# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Структура збереження сповіщень:
# chat_id → список job_id
user_jobs = {}

# Базовий URL для отримання цін
PRICE_API_URL = 'https://api.coinlore.net/api/tickers/'

def fetch_price(symbol: str) -> float | None:
    """Повертає поточну ціну symbol або None, якщо не знайдено."""
    resp = requests.get(PRICE_API_URL, params={'start': 0, 'limit': 100})
    data = resp.json().get('data', [])
    for c in data:
        if c['symbol'].upper() == symbol.upper():
            return float(c['price_usd'])
    return None

def set_alert(message):
    """
    Очікує команду у форматі:
    /alert BTC above 70000 hourly
    /alert ETH below 1500 daily
    """
    parts = message.text.split()
    if len(parts) != 5 or parts[0] != '/alert':
        bot.send_message(
            message.chat.id,
            "Невірний формат.\n"
            "Використання:\n"
            "/alert <SYMBOL> <above|below> <threshold> <hourly|daily>\n"
            "Приклад: /alert BTC above 70000 hourly"
        )
        return

    _, symbol, direction, threshold_str, interval = parts
    try:
        threshold = float(threshold_str)
    except ValueError:
        bot.send_message(message.chat.id, "Поріг має бути числом.")
        return

    if direction not in ('above', 'below'):
        bot.send_message(message.chat.id, "Вкажіть direction: above або below.")
        return
    if interval not in ('hourly', 'daily'):
        bot.send_message(message.chat.id, "Інтервал: hourly або daily.")
        return

    # Ідентифікатор job'и
    job_id = f"alert_{message.chat.id}_{symbol}_{direction}_{threshold}_{interval}"

    # Якщо вже існує — видаляємо стару
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass

    def job_func():
        price = fetch_price(symbol)
        if price is None:
            bot.send_message(message.chat.id, f"Не знайдено монету {symbol}.")
            return

        if (direction == 'above' and price > threshold) or \
           (direction == 'below' and price < threshold):
            bot.send_message(
                message.chat.id,
                f"🔔 {symbol} зараз {price}$, що "
                f"{'вище' if direction=='above' else 'нижче'} за {threshold}$"
            )
            # якщо сповіщення одноразове — раскоментуйте наступний рядок
            # scheduler.remove_job(job_id)

    # Додаємо job
    if interval == 'hourly':
        scheduler.add_job(job_func, 'interval', hours=1, id=job_id)
    else:  # daily
        scheduler.add_job(job_func, 'interval', days=1, id=job_id)

    # Зберігаємо
    user_jobs.setdefault(message.chat.id, []).append(job_id)

    bot.send_message(
        message.chat.id,
        f"✅ Сповіщення встановлено:\n"
        f"{symbol} {direction} {threshold}$ кожні {interval}."
    )

def list_alerts(message):
    """Виводить список активних сповіщень дружнім текстом."""
    jobs = user_jobs.get(message.chat.id, [])
    if not jobs:
        bot.send_message(message.chat.id, "У вас немає активних сповіщень.")
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
    bot.send_message(message.chat.id, text)

def remove_alert(message):
    """
    Очікує команду:
    /remove_alert <job_id>
    """
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Використання: /remove_alert <job_id>")
        return
    job_id = parts[1].strip()
    try:
        scheduler.remove_job(job_id)
        user_jobs[message.chat.id].remove(job_id)
        bot.send_message(message.chat.id, f"Сповіщення {job_id} видалено.")
    except Exception:
        bot.send_message(message.chat.id, f"Не вдалося видалити {job_id}.")

def schedule_alert(chat_id, symbol, direction, threshold, interval):
    """
    Створює job і повертає job_id.
    """
    job_id = f"alert_{chat_id}_{symbol}_{direction}_{threshold}_{interval}"
    # видаляємо старий, якщо є
    try: scheduler.remove_job(job_id)
    except: pass

    def job_func():
        price = fetch_price(symbol)
        if price is None: 
            bot.send_message(chat_id, f"Coin {symbol} not found.")
            return
        cond = (direction=='above' and price>threshold) or \
               (direction=='below' and price< threshold)
        if cond:
            bot.send_message(chat_id,
                f"🔔 {symbol} is now {price}$, "
                f"{'above' if direction=='above' else 'below'} {threshold}$"
            )
    # розклад
    if interval == 'minutely':
        scheduler.add_job(job_func, 'interval', minutes=1, id=job_id)
    elif interval == 'hourly':
        scheduler.add_job(job_func, 'interval', hours=1, id=job_id)
    else:  # daily
        scheduler.add_job(job_func, 'interval', days=1, id=job_id)

    user_jobs.setdefault(chat_id, []).append(job_id)
    return job_id

def cancel_alert(chat_id: int, job_id: str):
    """
    Видаляє сповіщення за job_id та надсилає дружнє підтвердження.
    """
    try:
        scheduler.remove_job(job_id)
        user_jobs.get(chat_id, []).remove(job_id)
        parts = job_id.split('_', 5)
        if len(parts) == 6:
            _, _, symbol, direction, threshold, _ = parts
            bot.send_message(
                chat_id,
                f"🗑️ Alert removed: {symbol} {direction} {threshold}$"
            )
        else:
            bot.send_message(chat_id, f"🗑️ Alert {job_id} removed.")
    except Exception:
        bot.send_message(chat_id, "⚠️ Не вдалося видалити сповіщення.")

