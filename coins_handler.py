import requests
from telebot import types
from notifications_handler import bot
from telebot.types import InputMediaPhoto

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

def coin_info_handler(call: types.CallbackQuery):
    chat_id    = call.message.chat.id
    msg_id     = call.message.message_id
    sym        = call.data.split('_', 1)[1]   # наприклад 'BTC'
    cid        = COIN_LORE_IDS.get(sym)
    if not cid:
        bot.answer_callback_query(call.id, "Не знайдено монету.")
        return

    # 1) Дані з CoinLore
    url  = f'https://api.coinlore.net/api/ticker/?id={cid}'
    resp = requests.get(url)
    data = resp.json()[0]
    price  = data['price_usd']
    ch24   = data.get('percent_change_24h', 0)
    ch7d   = data.get('percent_change_7d', 0)
    vol24  = data.get('volume24', '—')

    # 2) Графік за 1 день через Chart-Img
    chart_url = (
        f'https://api.chart-img.com/v1/tradingview/mini-chart'
        f'?key={CHARTS_KEY}'
        f'&symbol=BINANCE:{sym}USD'
        f'&interval=1D&width=600&height=400&theme=light'
    )
    img = requests.get(chart_url).content

    # 3) Формуємо підпис
    caption = (
        f"{data['name']} ({sym})\n\n"
        f"💲 Price: {price}$\n"
        f"📈 24h: {round(float(ch24),2)}%\n"
        f"📈 7d:  {round(float(ch7d),2)}%\n"
        f"🔄 24h Volume: {vol24}$"
    )

    # 4) Створюємо клавіатуру «Назад»
    back_markup = types.InlineKeyboardMarkup()
    back_markup.add(
        types.InlineKeyboardButton('« Назад', callback_data='coin_back_to_menu')
    )

    # 5) Редагуємо те саме повідомлення, підставляючи media + caption + кнопку Назад
    media = InputMediaPhoto(media=img, caption=caption)
    bot.edit_message_media(
        media=media,
        chat_id=chat_id,
        message_id=msg_id,
        reply_markup=back_markup
    )
