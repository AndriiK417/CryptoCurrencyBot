from telebot import types

# Ті ж монети, що й у charts_markup
coins = [
    ('Bitcoin','BTCUSD'),('Ethereum','ETHUSD'),('Tether','APTUSDT'),
    ('BNB','BNBUSD'),('XRP','XRPUSD'),('USD Coin','USDCUSDT'),
    ('Lido Stacked Ether','LDOUSD'),('Dogecoin','DOGEUSD'),
    ('Cardano','ADAUSD'),('Solana','SOLUSD')
]

alert_coins_markup = types.InlineKeyboardMarkup(row_width=2)
buttons = [types.InlineKeyboardButton(name, callback_data=f'alert_coin_{sym}') 
           for name,sym in coins]
alert_coins_markup.add(*buttons)
