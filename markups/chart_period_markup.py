from telebot import types

def get_chart_period_markup(coin: str) -> types.InlineKeyboardMarkup:
    """
    Повертає InlineKeyboardMarkup з кнопками для вибору періоду графіка:
    1D, 1M, 3M, 1Y
    """
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('1 день',   callback_data=f'chart_{coin}_1D'),
        types.InlineKeyboardButton('1 місяць', callback_data=f'chart_{coin}_1M'),
        types.InlineKeyboardButton('3 місяці', callback_data=f'chart_{coin}_3M'),
        types.InlineKeyboardButton('1 рік',     callback_data=f'chart_{coin}_1Y'),
    )
    return markup
