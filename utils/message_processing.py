# Функции для удаления сообщений бота
from telegram.ext import ContextTypes
from telegram import Message, Update
from telegram.error import BadRequest
from utils.logger import logger


async def save_ids_message_for_delete(context: ContextTypes.DEFAULT_TYPE, *args: Message) -> None:
    """

    Args:
        context:
        *args: сообщения которые нужно в дальнейшем удалить

    Returns: сохраняет в контекст id сообщений которые нужно будет удалить

    """
    if type(context.user_data.get('message_ids_to_delete')) != list:
        context.user_data['message_ids_to_delete'] = []

    message_ids_to_delete = context.user_data.get('message_ids_to_delete')
    for message in args:
        # todo если в ответе отправки сообщения будет ошибка? будет ли у сообщения id  и как эту ситуацию обрабатывать
        message_ids_to_delete.append(message.id)


async def delete_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """

    Args:
        update:
        context:

    Returns: удаляет сообщения по id и очищает очередь удаления

    """
    message_ids_to_delete = context.user_data.get('message_ids_to_delete')
    if not message_ids_to_delete:
        return
    for message_id in message_ids_to_delete[::-1]:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
        except BadRequest:
            logger.error(f'delete_message BadRequest user_id:{update.effective_chat.id}')

    # очистить список сообщений на удаление
    context.user_data['message_ids_to_delete'] = []
