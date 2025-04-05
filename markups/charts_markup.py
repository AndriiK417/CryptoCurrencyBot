from telebot import types

charts_markup = types.InlineKeyboardMarkup()
variant1 = types.InlineKeyboardButton('Bitcoin', callback_data='BTCUSD')
variant2 = types.InlineKeyboardButton('Ethereum', callback_data='ETHUSD')
variant3 = types.InlineKeyboardButton('Tether', callback_data='APTUSDT') #?
variant4 = types.InlineKeyboardButton('BNB', callback_data='BNBUSD') 
variant5 = types.InlineKeyboardButton('XRP', callback_data='XRPUSD') #?
variant6 = types.InlineKeyboardButton('USD Coin', callback_data='USDCUSDT') #?
variant7 = types.InlineKeyboardButton('Lido Stacked Ether', callback_data="LDOUSD")
variant8 = types.InlineKeyboardButton('Dogecoin', callback_data="DOGEUSD")
variant9 = types.InlineKeyboardButton('Cardano', callback_data="ADAUSD")
variant10 = types.InlineKeyboardButton('Solana', callback_data="SOLUSD")

charts_markup.add(variant1, variant2, variant3, variant4, variant5, variant6, variant7, variant8, variant9, variant10)