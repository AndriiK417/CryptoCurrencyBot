from telebot import types

# 1) Меню вибору монети для графіка
coins_markup = types.InlineKeyboardMarkup()
# тепер callback_data починається з selectchart_
coin1  = types.InlineKeyboardButton('Bitcoin',    callback_data='coininfo_BTC')
coin2  = types.InlineKeyboardButton('Ethereum',   callback_data='coininfo_ETH')
coin3  = types.InlineKeyboardButton('Tether',     callback_data='coininfo_USDT')
coin4  = types.InlineKeyboardButton('BNB',        callback_data='coininfo_BNB')
coin5  = types.InlineKeyboardButton('XRP',        callback_data='coininfo_XRP')
coin6  = types.InlineKeyboardButton('USD Coin',   callback_data='coininfo_USDC')
coin7  = types.InlineKeyboardButton('LDO',        callback_data='coininfo_LDO')
coin8  = types.InlineKeyboardButton('Dogecoin',   callback_data='coininfo_DOGE')
coin9  = types.InlineKeyboardButton('Cardano',    callback_data='coininfo_ADA')
coin10 = types.InlineKeyboardButton('Solana',     callback_data='coininfo_SOL')

coins_markup.add(
    coin1, coin2, coin3, coin4, coin5, coin6, coin7, coin8, coin9, coin10
)

