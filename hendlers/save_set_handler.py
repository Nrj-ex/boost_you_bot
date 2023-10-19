from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (MessageHandler, ContextTypes, CallbackQueryHandler,
                          filters, ConversationHandler)

from constants import CANCEL_SAVE_SET, CONFIRM_SAVING, SET_EXERCISE_NAME, WAIT_SOLUTION

from classes import Exercise
from loader import storage
from utils import logger

EXERCISE_KEYS_LIST = storage.get_exercise_list()


async def choose_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None | int:
    """Send a message when the command /help is issued."""
    user = update.effective_user
    exercise = Exercise(user_id=user.id)
    # сохранить количество повторений
    if update.message.text.split()[0].isdigit():
        # первое число считается количеством повторений
        count = int(update.message.text.split()[0])
        if count > 999:
            await context.bot.send_message(chat_id=user.id, text='Обманываешь сам себя')
            return ConversationHandler.END
        exercise.count = count
    else:
        logger.error(f'''Количество повторений не найдено! message_text: "{update.message.text}"''')
        await context.bot.send_message(chat_id=user.id,
                                       text='Количество не распознано!\nВведите количество выполненных повторений(цифрами)')
        return ConversationHandler.END

    context.user_data['exercise'] = exercise

    keyboard = []
    # todo язык пока захардкожен, позже брать из настроек пользователя
    exercises = storage.get_exercise_list(language='ru')
    for key, exercise in exercises.items():
        if not keyboard or len(keyboard) < 2 or len(keyboard[-1]) % 2 == 0:
            keyboard.append([InlineKeyboardButton(exercise, callback_data=key)])
        else:
            keyboard[-1].append(InlineKeyboardButton(exercise, callback_data=key))
            # отжимания и прес мне удобнее справа ;)
            keyboard[-1] = keyboard[-1][::-1]

    keyboard.append([InlineKeyboardButton('❌Cancel', callback_data=CANCEL_SAVE_SET)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=user.id, text=f'Количество: {exercise.count}', reply_markup=reply_markup)
    return SET_EXERCISE_NAME


async def set_exercise_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    query = update.callback_query
    exercise = context.user_data.get('exercise')
    if not exercise or not isinstance(exercise, Exercise):
        # Если нет упражнения выход
        error_text = "Error: Упражнение не найдено.\nПопробуйте заново"
        await context.bot.send_message(chat_id=user.id, text=error_text)
        await cancel_save_set(update, context)

    exercise.id = int(query.data.split('_')[1])
    exercise.name = EXERCISE_KEYS_LIST.get(query.data)

    # клавиатура да/нет
    # todo добавить кнопку "ввести вес" когда нибудь, может быть
    keyboard = [
        [
            InlineKeyboardButton('❌NO', callback_data=CANCEL_SAVE_SET),
            InlineKeyboardButton('✅YES', callback_data=CONFIRM_SAVING),
        ]
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
                                       text=f"Подход: {exercise.show()}\nСохранён!")

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
    await update.callback_query.delete_message()
    context.user_data.clear()
    await context.bot.send_message(chat_id=update.effective_user.id, text="Отменено")
    return ConversationHandler.END


# сохранить упражнение
save_set_handler = ConversationHandler(
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
                CallbackQueryHandler(save_set_exercise, pattern="^" + CONFIRM_SAVING + "$")
            ],

    },
    fallbacks=[
        CallbackQueryHandler(cancel_save_set, pattern="^" + CANCEL_SAVE_SET + "$")
    ],
    conversation_timeout=600,
)
