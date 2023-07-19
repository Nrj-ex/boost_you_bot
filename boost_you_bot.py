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
    CallbackQueryHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

from database.database_class import Database
from users_storage import UsersStorage

memes_db = Database()
users = UsersStorage(memes_db)


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


async def get_insult(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user_id = update.effective_user.id

    keyboard = [
        [InlineKeyboardButton('NEXT_INSULT', callback_data=str(NEXT_INSULT))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=user_id, text=genins(), reply_markup=reply_markup)


async def button_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()

    if query.data == 'start':
        await start(context, update)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.

    application = Application.builder().token(config.token).rate_limiter(
        AIORateLimiter(overall_max_rate=10, max_retries=3)).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    application.add_handler(CallbackQueryHandler(button_options))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
