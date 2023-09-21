from utils.logger import logger
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
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, AIORateLimiter, \
    CallbackQueryHandler

from hendlers.start import start
from hendlers.help import help
from hendlers.about import about
from hendlers.show_user_statistics import show_user_statistics_handler
from hendlers.save_set_handler import save_set_handler


async def button_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.delete_message()
    await context.bot.send_message(chat_id=update.effective_user.id, text='Кнопка устарела и была удалена')


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.

    application = Application.builder().token(config.token).rate_limiter(
        AIORateLimiter(overall_max_rate=10, max_retries=3)).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(show_user_statistics_handler)
    application.add_handler(save_set_handler)
    application.add_handler(CallbackQueryHandler(button_options))

    application.run_polling()


if __name__ == "__main__":
    main()
