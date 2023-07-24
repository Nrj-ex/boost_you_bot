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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

from database.database_class import Database
from users_storage import UsersStorage

memes_db = Database()
users = UsersStorage(memes_db)

CANCEL_SAVE_SET, CONFIRM_SAVING, SET_EXERCISE_NAME, WAIT_SOLUTION = range(4)
# todo получать список из базы
exercise_list = ['qqq', 'www', 'eee']


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""

    user = update.effective_user
    users.add_user(user=user)
    keyboard = [
        [InlineKeyboardButton('start', callback_data='start')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=user.id, text=f"Hi!", reply_markup=reply_markup)


async def choose_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user = update.effective_user
    # todo сохранить количество
    context.user_data['exercise'] = [update.message.text]

    exercise_buttons = []
    for exercise in exercise_list:
        exercise_buttons.append(InlineKeyboardButton(exercise, callback_data=exercise))

    keyboard = [
        exercise_buttons,
        [InlineKeyboardButton('Cancel', callback_data=str(CANCEL_SAVE_SET))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=user.id, text=update.message.text, reply_markup=reply_markup)
    return SET_EXERCISE_NAME


async def set_exercise_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # todo сохранение в юзер дату названия упражнения
    user = update.effective_user
    query = update.callback_query
    if context.user_data.get('exercise'):
        context.user_data['exercise'].append(query.data)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"set_exercise_name {query.data}")
    text = context.user_data.get('exercise')
    print(text)
    # клавиатура да/нет
    keyboard = [
        [InlineKeyboardButton('Сохранить', callback_data=str(CONFIRM_SAVING))],
        [InlineKeyboardButton('Cancel', callback_data=str(CANCEL_SAVE_SET))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # выводить выбранное упражнение и количество
    await context.bot.send_message(chat_id=user.id, text='confirm_saving', reply_markup=reply_markup)

    return WAIT_SOLUTION




async def save_set_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # todo сохранение в бд
    await context.bot.send_message(chat_id=update.effective_user.id,
                                   text=f"save_set_exercise {str(context.user_data.get('exercise'))}")

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_save_set(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # todo сообщение что сохранение отменено
    context.user_data.clear()
    await context.bot.send_message(chat_id=update.effective_user.id, text="cancel_save_set")
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
    # application.add_handler(CommandHandler("help", test))

    # сохранить упражнение
    save_sets = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & ~filters.COMMAND, choose_exercise),
        ],
        states={
            SET_EXERCISE_NAME:
                [
                    CallbackQueryHandler(set_exercise_name, pattern="^" + exercise + "$") for exercise in exercise_list
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

    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    application.add_handler(CallbackQueryHandler(button_options))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
