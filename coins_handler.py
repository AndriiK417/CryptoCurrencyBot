import requests
from notifications_handler import bot

# Відповідність SYMBOL → CoinLore id
COIN_LORE_IDS = {
    'BTC': 90,
    'ETH': 80,
    'USDT': 825,   # приклад
    'BNB': 2710,
    'XRP': 58,
    'USDC': 48543,
    'LDO': 48447,
    'DOGE': 2,
    'ADA': 258,
    'SOL': 48543,  # уточніть id SOL, якщо потрібно
}

CHARTS_KEY = 'qJX6lruQMB9Yhkj7ub87z3vrFa8z6hI13AgoaLdS'

def coin_info_handler(call):
    chat = call.message.chat.id
    sym  = call.data.split('_',1)[1]  # наприклад 'BTC'
    cid  = COIN_LORE_IDS.get(sym)
    if not cid:
        bot.send_message(chat, f"Не знайдено монету {sym}.")
        return

    # 1) Дані з CoinLore
    url = f'https://api.coinlore.net/api/ticker/?id={cid}'
    resp = requests.get(url)
    if resp.status_code != 200:
        bot.send_message(chat, "Помилка API CoinLore.")
        return
    data = resp.json()[0]
    price     = data['price_usd']
    ch24      = data.get('percent_change_24h', 0)
    ch7d      = data.get('percent_change_7d', 0)
    vol24     = data.get('volume24', '—')

    # 2) Графік за 1 день через Chart-Img
    chart_url = (
        f'https://api.chart-img.com/v1/tradingview/mini-chart'
        f'?key={CHARTS_KEY}'
        f'&symbol=BINANCE:{sym}USD'   # BINANCE:BTCUSD etc.
        f'&interval=1D&width=600&height=400&theme=light'
    )
    img = requests.get(chart_url).content

    caption = (
        f"{data['name']} ({sym})\n\n"
        f"💲 Price: {price}$\n"
        f"📈 24h: {round(float(ch24),2)}%\n"
        f"📈 7d:  {round(float(ch7d),2)}%\n"
        f"🔄 24h Volume: {vol24}$"
    )

    bot.send_photo(chat, img, caption=caption)
