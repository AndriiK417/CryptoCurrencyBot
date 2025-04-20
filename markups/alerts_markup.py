from telebot import types
from notifications_handler import user_jobs

# 1) Головне меню Alerts
alert_menu_markup = types.InlineKeyboardMarkup(row_width=2)
alert_menu_markup.add(
    types.InlineKeyboardButton('➕ Add Alert',    callback_data='alert_add'),
    types.InlineKeyboardButton('📋 List Alerts',  callback_data='alert_list'),
    types.InlineKeyboardButton('❌ Remove Alert', callback_data='alert_remove'),
)

# 2) Вибір монети
coins = [
    ('Bitcoin','BTCUSD'),('Ethereum','ETHUSD'),('Tether','APTUSDT'),
    ('BNB','BNBUSD'),('XRP','XRPUSD'),('USD Coin','USDCUSDT'),
    ('Lido Stacked Ether','LDOUSD'),('Dogecoin','DOGEUSD'),
    ('Cardano','ADAUSD'),('Solana','SOLUSD')
]
alert_coins_markup = types.InlineKeyboardMarkup(row_width=2)
alert_coins_markup.add(
    *[types.InlineKeyboardButton(name, callback_data=f'alert_coin_{sym}')
      for name,sym in coins]
)
alert_coins_markup.add(types.InlineKeyboardButton('« Назад', callback_data='alert_back_to_menu'))

# 3) Вибір напрямку
alert_direction_markup = types.InlineKeyboardMarkup(row_width=2)
alert_direction_markup.add(
    types.InlineKeyboardButton('🔼 Above', callback_data='alert_dir_above'),
    types.InlineKeyboardButton('🔽 Below', callback_data='alert_dir_below'),
)
alert_direction_markup.add(types.InlineKeyboardButton('« Назад', callback_data='alert_back_to_coin'))

# Вибір threshold
alert_threshold_markup = types.InlineKeyboardMarkup(row_width=2)
alert_threshold_markup.add(types.InlineKeyboardButton('« Назад', callback_data='alert_back_to_direction'))

# 4) Вибір інтервалу
alert_interval_markup = types.InlineKeyboardMarkup(row_width=2)
alert_interval_markup.add(
    types.InlineKeyboardButton('1 minute', callback_data='alert_int_minutely'),
    types.InlineKeyboardButton('1 Hour', callback_data='alert_int_hourly'),
    types.InlineKeyboardButton('1 Day',  callback_data='alert_int_daily'),
)
alert_interval_markup.add(types.InlineKeyboardButton('« Назад', callback_data='alert_back_to_threshold'))

# 5) Меню видалення alert-ів
def get_remove_alerts_markup(chat_id: int) -> types.InlineKeyboardMarkup:
    """
    Повертає InlineKeyboardMarkup, в якому кожен alert — окрема кнопка з дружнім
    лейблом, наприклад "BTCUSD above 90000.0$".
    callback_data = 'alert_rm_<job_id>'
    """
    markup = types.InlineKeyboardMarkup(row_width=1)
    for job_id in user_jobs.get(chat_id, []):
        parts = job_id.split('_', 5)
        if len(parts) == 6:
            _, _, symbol, direction, threshold, _ = parts
            label = f"{symbol} {direction} {threshold}$"
        else:
            label = job_id
        markup.add(
            types.InlineKeyboardButton(label, callback_data=f'alert_rm_{job_id}')
        )
    markup.add(types.InlineKeyboardButton('« Назад', callback_data='alert_back_to_menu'))
    return markup

