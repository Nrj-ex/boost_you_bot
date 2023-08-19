import logging
import config

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, AIORateLimiter, \
    CallbackQueryHandler, MessageHandler, filters, ConversationHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARNING,
)
# filename="bot_log.log"
logger = logging.getLogger(__name__)

from database.database_class import Database
from classes.users_storage import Storage

memes_db = Database()
storage = Storage(memes_db)

(CANCEL_SAVE_SET, CONFIRM_SAVING, SET_EXERCISE_NAME, WAIT_SOLUTION,
 START_SHOW_USER_STATISTICS, WAIT_SELECT_TIME_PERIOD, CANCEL_SHOW_USER_STATISTICS,
 DAY, WEEK, MONTH, ALLTIME) = range(1, 12)
EXERCISE_KEYS_LIST = storage.get_exercise_list()
from classes.exercise_class import Exercise


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""

    user = update.effective_user
    storage.add_user(user=user)
    keyboard = [
        [InlineKeyboardButton('start', callback_data='start')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=user.id, text=f"Hi!", reply_markup=reply_markup)


async def choose_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None | int:
    """Send a message when the command /help is issued."""
    user = update.effective_user
    exercise = Exercise(user_id=user.id)
    # сохранить количество повторений
    if update.message.text.split()[0].isdigit():
        # первое число считается количеством повторений
        count = int(update.message.text.split()[0])
        exercise.count = count
    else:
        logger.error(f'''Количество повторений не найдено! message_text: "{update.message.text}"''')
        return await cancel_save_set(update, context)

    context.user_data['exercise'] = exercise

    keyboard = []
    # todo язык пока захардкожен, позже брать из настроек пользователя
    exercises = storage.get_exercise_list(language='ru')
    for key, exercise in exercises.items():
        keyboard.append([InlineKeyboardButton(exercise, callback_data=key)])

    keyboard.append([InlineKeyboardButton('Cancel', callback_data=str(CANCEL_SAVE_SET))])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=user.id, text=update.message.text, reply_markup=reply_markup)
    return SET_EXERCISE_NAME


async def set_exercise_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    query = update.callback_query
    exercise = context.user_data.get('exercise')
    if not exercise or not isinstance(exercise, Exercise):
        # Если нету упражнения выход
        error_text = "Error: Упражнение не найдено.\nПопробуйте заново"
        await context.bot.send_message(chat_id=user.id, text=error_text)
        await cancel_save_set(update, context)

        # context.user_data['exercise'].append(query.data)
    exercise.id = int(query.data.split('_')[1])
    exercise.name = EXERCISE_KEYS_LIST.get(query.data)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"set_exercise_id: {exercise.id}")

    # клавиатура да/нет
    # todo добавить кнопку "ввести вес" когда нибудь, может быть
    keyboard = [
        [InlineKeyboardButton('Save', callback_data=str(CONFIRM_SAVING))],
        [InlineKeyboardButton('Cancel', callback_data=str(CANCEL_SAVE_SET))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=user.id, text=f'Сохранить подход:\n{exercise.show()}',
                                   reply_markup=reply_markup)

    return WAIT_SOLUTION


async def save_set_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    :return: сохраняет упражнение в базу
    """
    from classes.exercise_class import Exercise
    exercise = context.user_data.get('exercise')
    if exercise and isinstance(exercise, Exercise):
        storage.save_exercise(exercise)
        await context.bot.send_message(chat_id=update.effective_user.id,
                                       text=f"Подход сохранен")

    else:
        logger.error(f'''Упражнение не найдено: context.user_data:"{context.user_data}"''')
        await context.bot.send_message(chat_id=update.effective_user.id,
                                       text=f"ошибка упражнение не найдено, попробуйте снова")

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_save_set(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    :return: Отмена сохранения сообщения
    """
    context.user_data.clear()
    await context.bot.send_message(chat_id=update.effective_user.id, text="Отмена")
    return ConversationHandler.END


async def select_time_period(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # вывести выбор периода
    return WAIT_SELECT_TIME_PERIOD


async def show_user_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # вывод статистики в зависимости от выбора пользователя
    # одна функция что бы получать статискику в которую будет передаваться период для запроса в бд
    return ConversationHandler.END


async def cancel_show_user_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await context.bot.send_message(chat_id=update.effective_user.id, text="cancel_show_user_statistics")
    return ConversationHandler.END


async def button_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    # if query.data in exercise_list:

    #     await test(update, context)
    #     pass


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.

    application = Application.builder().token(config.token).rate_limiter(
        AIORateLimiter(overall_max_rate=10, max_retries=3)).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    # todo add command /statistics - старт сценария показа статистики
    # todo добавить меню инлайн кнопки [hepl][my_statistics]
    # application.add_handler(CommandHandler("help", test))

    # сохранить упражнение
    save_sets = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & ~filters.COMMAND, choose_exercise),
        ],
        states={
            SET_EXERCISE_NAME:
                [
                    CallbackQueryHandler(set_exercise_name, pattern="^" + exercise + "$") for exercise in
                    EXERCISE_KEYS_LIST.keys()
                ],
            WAIT_SOLUTION:
                [
                    CallbackQueryHandler(save_set_exercise, pattern="^" + str(CONFIRM_SAVING) + "$")
                ],

        },

        fallbacks=[
            CallbackQueryHandler(cancel_save_set, pattern="^" + str(CANCEL_SAVE_SET) + "$")
        ],
        conversation_timeout=600,
    )
    application.add_handler(save_sets)

    # todo вывод статистики упражнений
    # кнопка: показать статистику
    # выберите период:
    # [день][неделя][месяц][все время]
    # [отмена]
    # вывод статистики
    show_user_statistics_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(select_time_period, pattern="^" + str(START_SHOW_USER_STATISTICS) + "$")
        ],
        states={
            WAIT_SELECT_TIME_PERIOD:
                [
                    CallbackQueryHandler(show_user_statistics, pattern="^" + str(period) + "$") for period in
                    (DAY, WEEK, MONTH, ALLTIME)
                ],

        },

        fallbacks=[
            CallbackQueryHandler(cancel_show_user_statistics, pattern="^" + str(CANCEL_SHOW_USER_STATISTICS) + "$")
        ],
        conversation_timeout=600,
    )
    application.add_handler(show_user_statistics_handler)

    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    application.add_handler(CallbackQueryHandler(button_options))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
