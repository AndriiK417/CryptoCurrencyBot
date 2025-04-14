from telebot import types
from notifications_handler import user_jobs

def get_remove_alerts_markup(chat_id: int) -> types.InlineKeyboardMarkup:
    """
    Повертає InlineKeyboardMarkup, в якому кожен alert — окрема кнопка.
    callback_data = 'alert_rm_<job_id>'
    А текст кнопки — '<SYMBOL> <direction> <threshold>$'
    """
    markup = types.InlineKeyboardMarkup(row_width=1)
    jobs = user_jobs.get(chat_id, [])
    for job_id in jobs:
        # job_id формат: 'alert_<chat>_<symbol>_<direction>_<threshold>_<interval>'
        parts = job_id.split('_', 5)
        if len(parts) == 6:
            _, _, symbol, direction, threshold, _interval = parts
            label = f"{symbol} {direction} {threshold}$"
        else:
            # на випадок незвичайного формату
            label = job_id
        markup.add(
            types.InlineKeyboardButton(label, callback_data=f'alert_rm_{job_id}')
        )
    return markup
