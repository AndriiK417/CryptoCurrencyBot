import telebot
import requests
from markups.markup import markup
from markups.charts_markup import charts_markup
from markups.currency_markup import currency_markup
from markups.price_changes_markup import price_changes_markup
from markups.period_markup import period_markup
from markups.coins_markup import coins_markup
from alerts_handler import show_alert_menu


API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)

# для пагінації: скільки пропустити
skip_currency = 0
skip_price = 0

# Базовий URL CoinLore
BASE_URL = 'https://api.coinlore.net/api/tickers/'

def commands_handler(message):
    global skip_currency, skip_price
    skip_currency = 0
    skip_price = 0

    if message.chat.type == 'private':
        if message.text == 'Currency':
            # ?start=0&limit=10
            resp = requests.get(BASE_URL, params={'start': skip_currency, 'limit': 10})
            coins = resp.json().get('data', [])
            text = '\n'.join(
                f"{c['name']} — {round(float(c['price_usd']), 3)}$"
                for c in coins
            )

            bot.send_message(message.chat.id, text, reply_markup=currency_markup)

        elif message.text == 'Price changes':
            bot.send_message(message.chat.id, "Choose period:", reply_markup=period_markup)

        elif message.text == 'Charts':
            bot.send_message(message.chat.id, "Choose the crypto-chart you need:", reply_markup=charts_markup)
        
        elif message.text == 'Монети':
            bot.send_message(message.chat.id, "Оберіть монету:", reply_markup=coins_markup)

        elif message.text == 'Alerts':
            show_alert_menu(message)

def start(message):
    """
    Стартове вітання + короткий гід по кнопках.
    """
    user = message.from_user.first_name or 'there'
    text = (
        f"👋 Hi, {user}!\n\n"
        "Ось що я вмію:\n"
        "• <b>Монети</b> — показує детальну інформацію по вибраній монеті (ціна, зміни у відсотках, графік за день) в одному місці;\n"
        "• <b>Currency</b> — показує поточні ціни найпопулярніших 10 монет;\n"
        "• <b>Price changes</b> — показує відсоткові зміни цін монет за 1 год, 1 день або 1 тиждень;\n"
        "• <b>Charts</b> — показує графіки криптовалют за різні періоди (1 день, 1 місяць, 3 місяці, 1 рік);\n"
        "• <b>Alerts</b> — створює сповіщення, коли ціна монети вийде за обрану межу/зміниться на вибраний відсоток.\n\n"
        "Просто натисніть відповідну кнопку нижче 👇"
    )
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='HTML',
        reply_markup=markup
    )
