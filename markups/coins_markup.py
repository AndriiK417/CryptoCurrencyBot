from telebot import types

coins = [
    ('Bitcoin',    'BTC'),
    ('Ethereum',   'ETH'),
    ('Tether',     'USDT'),
    ('BNB',        'BNB'),
    ('XRP',        'XRP'),
    ('USD Coin',   'USDC'),
    ('LDO',        'LDO'),
    ('Dogecoin',   'DOGE'),
    ('Cardano',    'ADA'),
    ('Solana',     'SOL'),
]

coins_markup = types.InlineKeyboardMarkup(row_width=2)
for name, sym in coins:
    coins_markup.add(
        types.InlineKeyboardButton(name, callback_data=f'coininfo_{sym}')
    )
