from telegram import Update
from telegram.ext import ContextTypes
from init_storage import storage


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""

    user = update.effective_user
    text = '''Бот заменяет тетрадку в которую вы записываете выполненные упражнения после каждого подхода.\n'''

    text += 'Список поддерживаемых упражнений:\n'
    for i, e in enumerate(storage.get_exercise_list().values(), start=1):
        text += f'{i}. {e}\n'
    text += '\nДля сохранения подхода отправьте боту количество выполненных упражнений(число), затем выберите упражнение и нажмите сохранить.\n\n'
    text += '/statistic - показать статистику\n'

    await context.bot.send_message(chat_id=user.id, text=text)
