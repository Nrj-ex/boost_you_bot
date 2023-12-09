from uuid import uuid4
from telegram import (InlineQueryResultArticle, InputTextMessageContent,
                      InlineQueryResultsButton, Update, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from loader import storage


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""

    storage.add_user(user=update.effective_user)

    if update.inline_query.query.isdigit():
        selected_period = int(update.inline_query.query)
    else:
        selected_period = 0

    delta = timedelta(days=-selected_period)
    start_data = (datetime.now() + delta).date()
    statistic = ''

    if selected_period >= 99999:
        statistic += f'За все время\n'
    elif selected_period == 0:
        statistic += f'{start_data}\n'
    else:
        statistic += f'C {start_data} по {datetime.now().date()}\n'

    statistic += f'{update.effective_user.name} выполнил(а):\n'

    user_statistic = storage.get_user_statistic(update.effective_user.id, start_data)
    if user_statistic:
        statistic += f'Название: количество / подходы \n'
        for exercise_name, count, sets in user_statistic:
            statistic += f'{exercise_name}: {count} / {sets}\n'
    else:
        statistic = 'НИ ЧЕ ГО 🤡️️️️️️'

    statistic += '\n© @Boostyou_bot'

    keyboard = [
        [InlineKeyboardButton('Показать свою статистику',
                              switch_inline_query_current_chat='0')],

    ]


    await update.inline_query.answer([
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="show my stats",
            input_message_content=InputTextMessageContent(statistic),
            description=f"Your stats for {selected_period} days",
            reply_markup=InlineKeyboardMarkup(keyboard),

        ),
    ], cache_time=0, is_personal=True,
        # кнопка перехода в бота, разобраться в стартовом параметре и возможностью добавить ссылку на другой канал
        button=InlineQueryResultsButton(text='Перейти в бота', start_parameter='start')

    )
