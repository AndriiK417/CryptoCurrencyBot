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
    """
    Повертає поточну ціну символу або None, якщо не знайдено.
    Підтримує символи виду 'BTC', 'BTCUSD', 'BTCUSDT' тощо.
    """
    # 1) нормалізуємо символ до базового (без USD/USDT)
    base = symbol.upper()
    if base.endswith("USDT"):
        base = base[:-4]
    elif base.endswith("USD"):
        base = base[:-3]

    # 2) робимо запит
    resp = requests.get(PRICE_API_URL, params={'start': 0, 'limit': 100})
    data = resp.json().get('data', [])

    # 3) шукаємо монету з символом base
    for c in data:
        if c['symbol'].upper() == base:
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


def schedule_alert(chat_id, symbol, direction, threshold, interval, mode='absolute'):
    """
    Створює job і повертає job_id.
    """
    job_id = f"alert_{chat_id}_{symbol}_{mode}_{direction}_{threshold}_{interval}"
    # видаляємо старий, якщо є
    try: scheduler.remove_job(job_id)
    except: pass

    # для percent — зафіксуємо базову ціну
    base_price = None
    if mode=='percent':
        base_price = fetch_price(symbol)

    def job_func():
        price = fetch_price(symbol)
        if price is None: return

        cond = False
        if mode=='absolute':
            cond = (direction=='above' and price>threshold) or (direction=='below' and price<threshold)
        else:  # percent
            if base_price:
                change = (price - base_price)/base_price*100
                cond = (direction=='up'   and change>=threshold) or \
                       (direction=='down' and change<=-threshold)
        if cond:
            bot.send_message(
                chat_id,
                f"🔔 {symbol} зараз {price}$ | "
                + (f"{round(change,2)}%" if mode=='percent' else f"{price}$")
            )
            # якщо alert одноразовий — прибрати job:
            # scheduler.remove_job(job_id)
    # розклад
    if interval == 'minutely':
        scheduler.add_job(job_func, 'interval', minutes=1, id=job_id)
    elif interval == 'hourly':
        scheduler.add_job(job_func, 'interval', hours=1, id=job_id)
    else:  # daily
        scheduler.add_job(job_func, 'interval', days=1, id=job_id)

    user_jobs.setdefault(chat_id, []).append(job_id)
    return job_id

