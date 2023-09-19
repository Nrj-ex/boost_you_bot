from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, ContextTypes, CallbackQueryHandler,
                          filters, ConversationHandler)
from constants import START_SHOW_USER_STATISTICS, WAIT_SELECT_TIME_PERIOD, CANCEL_SHOW_USER_STATISTICS, SELECTED_PERIOD

from init_storage import storage


async def select_time_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [
            # InlineKeyboardButton('День', callback_data=DAY),
            # InlineKeyboardButton('Неделя', callback_data=WEEK),
            # InlineKeyboardButton('Месяц', callback_data=MONTH),
            InlineKeyboardButton('Всё время', callback_data=SELECTED_PERIOD + '99999'),
        ],
        [InlineKeyboardButton('Cancel', callback_data=CANCEL_SHOW_USER_STATISTICS)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=update.effective_user.id, text='Выберите период', reply_markup=reply_markup)
    # вывести выбор периода
    return WAIT_SELECT_TIME_PERIOD


async def show_user_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    statistic = ''
    selected_period = update.callback_query.data.replace(SELECTED_PERIOD, '', 1)
    if not selected_period.isdigit():
        await context.bot.send_message(chat_id=update.effective_user.id, text='Не удалось получить период времени')
        return ConversationHandler.END
    selected_period = int(selected_period)
    if selected_period >= 99999:
        statistic += f'{update.effective_user.name} за все время выполнил(а):\n'

    user_statistic = storage.get_user_statistic(update.effective_user, selected_period)
    for exercise_name, count in user_statistic:
        statistic += f'{exercise_name}: {count}\n'

    statistic += '\n© @Boostyou_bot'

    # вывод статистики
    if user_statistic:
        await context.bot.send_message(chat_id=update.effective_user.id, text=statistic)
    else:
        # статистики нету
        await context.bot.send_message(chat_id=update.effective_user.id, text='За выбранный период ничего нет!')
    # одна функция что бы получать статискику в которую будет передаваться период для запроса в бд
    return ConversationHandler.END


async def cancel_show_user_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.callback_query.delete_message()
    await context.bot.send_message(chat_id=update.effective_user.id, text='Отменено')
    return ConversationHandler.END


# вывод статистики
show_user_statistics_handler = ConversationHandler(
    entry_points=[
        CommandHandler("statistic", select_time_period),
        CallbackQueryHandler(select_time_period, pattern="^" + START_SHOW_USER_STATISTICS + "$")
    ],
    states={
        WAIT_SELECT_TIME_PERIOD:
            [
                CallbackQueryHandler(show_user_statistics, pattern="^" + SELECTED_PERIOD)
            ],
    },

    fallbacks=[
        CallbackQueryHandler(cancel_show_user_statistics, pattern="^" + CANCEL_SHOW_USER_STATISTICS + "$")
    ],
    conversation_timeout=600,
)
