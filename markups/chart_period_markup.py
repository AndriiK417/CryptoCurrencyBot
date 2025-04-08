from telebot import types

def get_chart_period_markup(coin: str) -> types.InlineKeyboardMarkup:
    """
    Повертає InlineKeyboardMarkup з кнопками для вибору періоду графіка.
    call_data буде у форматі 'chart_<COIN>_<PERIOD>'.
    """
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton('1 год',  callback_data=f'chart_{coin}_1h'),
        types.InlineKeyboardButton('1 день', callback_data=f'chart_{coin}_1d'),
        types.InlineKeyboardButton('1 тиж',  callback_data=f'chart_{coin}_1w'),
    )
    return markup
