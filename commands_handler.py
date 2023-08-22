import telebot
import requests
from telebot import types

API_TOKEN = '6388083417:AAFnoBZpLQkrrF95Bj9uq0nYma5EUt9qs1k'
bot = telebot.TeleBot(API_TOKEN)

CURRENCY_API_LINK = 'https://api.coinstats.app/public/v1/coins?skip=0&limit=10&currency=USD'

currency_markup = types.InlineKeyboardMarkup()
currency_markup.row_width = 2
currency_markup.add(types.InlineKeyboardButton("<", callback_data="previous_currency"),
types.InlineKeyboardButton(">", callback_data="next_currency"))

price_changes_markup = types.InlineKeyboardMarkup()
price_changes_markup.row_width = 2
price_changes_markup.add(types.InlineKeyboardButton("<", callback_data="previous_price_changes"),
types.InlineKeyboardButton(">", callback_data="next_price_changes"))

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

def reset_skip_currency():
    global skip_currency
    skip_currency = 0

def reset_skip_price():
    global skip_price
    skip_price = 0

def commands_handler(message):
    if message.chat.type == 'private':
        if message.text == 'Currency':
            response = requests.get(CURRENCY_API_LINK).json()['coins']
            response_message = ''

            for i in range(10):
                response_message += response[i]['name'] + ' - ' + str(round(response[i]['price'], 3)) + '$ \n'
                
            bot.send_message(message.chat.id, response_message, reply_markup=currency_markup)

            reset_skip_currency()

        elif message.text == 'Price changes':
            response = requests.get(CURRENCY_API_LINK).json()['coins']
            response_message = ''

            for i in range(10):
                response_message += response[i]['name'] + ": " + str(response[i]['priceChange1w']) + '% \n'
                
            bot.send_message(message.chat.id, response_message, reply_markup=price_changes_markup)
        
            reset_skip_price()

        elif message.text == 'Charts':
            bot.send_message(message.chat.id, "Choose the crypto-chart you need:", reply_markup=charts_markup)
