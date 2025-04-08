from telebot import types

charts_markup = types.InlineKeyboardMarkup()
# тепер callback_data починається з selectchart_
variant1  = types.InlineKeyboardButton('Bitcoin',               callback_data='selectchart_BTCUSD')
variant2  = types.InlineKeyboardButton('Ethereum',              callback_data='selectchart_ETHUSD')
variant3  = types.InlineKeyboardButton('Tether',                callback_data='selectchart_APTUSDT')
variant4  = types.InlineKeyboardButton('BNB',                   callback_data='selectchart_BNBUSD')
variant5  = types.InlineKeyboardButton('XRP',                   callback_data='selectchart_XRPUSD')
variant6  = types.InlineKeyboardButton('USD Coin',              callback_data='selectchart_USDCUSDT')
variant7  = types.InlineKeyboardButton('Lido Stacked Ether',    callback_data='selectchart_LDOUSD')
variant8  = types.InlineKeyboardButton('Dogecoin',              callback_data='selectchart_DOGEUSD')
variant9  = types.InlineKeyboardButton('Cardano',               callback_data='selectchart_ADAUSD')
variant10 = types.InlineKeyboardButton('Solana',                callback_data='selectchart_SOLUSD')

charts_markup.add(
    variant1, variant2, variant3, variant4, variant5,
    variant6, variant7, variant8, variant9, variant10
)
