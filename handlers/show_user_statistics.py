from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, ContextTypes, CallbackQueryHandler,
                          filters, ConversationHandler, MessageHandler)
from datetime import datetime, timedelta

from constants import START_SHOW_USER_STATISTICS, WAIT_SELECT_TIME_PERIOD, CANCEL_SHOW_USER_STATISTICS, SELECTED_PERIOD
from loader import storage
from utils import logger


async def select_time_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton('❌Cancel', callback_data=CANCEL_SHOW_USER_STATISTICS)],
        [
            InlineKeyboardButton('За месяц', callback_data=SELECTED_PERIOD + '30'),
            InlineKeyboardButton('Всё время', callback_data=SELECTED_PERIOD + '99999'),
        ],
        [
            InlineKeyboardButton('За неделю', callback_data=SELECTED_PERIOD + '7'),
            InlineKeyboardButton('Сегодня', callback_data=SELECTED_PERIOD + '0'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=update.effective_user.id,
                                   text='Выберите период или введите количество дней за который хотите получить статистику (0: сегодня)',
                                   reply_markup=reply_markup)
    # вывести выбор периода
    return WAIT_SELECT_TIME_PERIOD


async def show_user_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_period: int) -> int:
    delta = timedelta(days=-selected_period)
    start_data = (datetime.now() + delta).date()
    statistic = ''

    if selected_period >= 99999:
        statistic += f'За все время\n'
    elif selected_period == 0:
        statistic += f'За сегодня\n'
    else:
        statistic += f'C {start_data} по {datetime.now().date()}\n'

    statistic += f'{update.effective_user.name} выполнил(а):\n'

    statistic += f'Название: количество / подходы \n'

    user_statistic = storage.get_user_statistic(update.effective_user.id, start_data)
    for exercise_name, count, sets in user_statistic:
        statistic += f'{exercise_name}: {count} / {sets}\n'

    statistic += '\n© @Boostyou_bot'

    # вывод статистики
    if user_statistic:
        await context.bot.send_message(chat_id=update.effective_user.id, text=statistic)
    else:
        # статистики нету
        await context.bot.send_message(chat_id=update.effective_user.id, text='За выбранный период ничего нет!')
    return ConversationHandler.END


async def show_user_statistics_by_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.delete_message()
    number_days = update.callback_query.data.replace(SELECTED_PERIOD, '', 1)
    if not number_days.isdigit():
        await context.bot.send_message(chat_id=update.effective_user.id, text='Не удалось получить период времени')
        logger.error(f'''Не удалось получить период времени: "{update.message.text}"''')
        return ConversationHandler.END
    number_days = int(number_days)
    return await show_user_statistics(update, context, number_days)


async def show_user_statistics_by_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # первое число считается количеством дней за которое нужно отдать статистику
    if update.message.text.split()[0].isdigit():
        number_days = int(update.message.text.split()[0])
    else:
        await context.bot.send_message(chat_id=update.effective_user.id, text='Количество дней не распознано!')
        logger.error(f'''Количество дней не распознано! message_text: "{update.message.text}"''')
        return ConversationHandler.END

    return await show_user_statistics(update, context, number_days)


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
                CallbackQueryHandler(show_user_statistics_by_button, pattern="^" + SELECTED_PERIOD),
                MessageHandler(filters.TEXT & ~filters.COMMAND, show_user_statistics_by_text),
            ],
    },

    fallbacks=[
        CallbackQueryHandler(cancel_show_user_statistics, pattern="^" + CANCEL_SHOW_USER_STATISTICS + "$")
    ],
    conversation_timeout=600,
)
