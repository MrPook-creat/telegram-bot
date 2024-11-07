from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Шаги разговора
TITLE, DESCRIPTION, COMPANY, REQUIREMENTS, CONDITIONS, CONTACTS = range(6)


# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Хорошего дня! 🌞",
        reply_markup=ForceReply(selective=True),
    )
    await update.message.reply_text(
        "Нажмите кнопку, чтобы опубликовать вакансию.",
        reply_markup=ReplyKeyboardMarkup(
            [["Опубликовать вакансию"]], one_time_keyboard=True, resize_keyboard=True
        )
    )
    return TITLE


# Получение заголовка вакансии
async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['title'] = update.message.text
    await update.message.reply_text("Введите описание вакансии:")
    return DESCRIPTION


# Получение описания вакансии
async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['description'] = update.message.text
    await update.message.reply_text("Введите название компании:")
    return COMPANY


# Получение компании
async def receive_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['company'] = update.message.text
    await update.message.reply_text("Введите требования к кандидатам:")
    return REQUIREMENTS


# Получение требований
async def receive_requirements(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['requirements'] = update.message.text
    await update.message.reply_text("Введите условия работы:")
    return CONDITIONS


# Получение условий
async def receive_conditions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['conditions'] = update.message.text
    await update.message.reply_text("Введите контактные данные:")
    return CONTACTS


# Получение контактов и публикация вакансии
async def receive_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['contacts'] = update.message.text

    # Форматирование вакансии
    job_post = f"""
    Заголовок: {context.user_data['title']}
    Описание: {context.user_data['description']}
    Компания: {context.user_data['company']}
    Требования: {context.user_data['requirements']}
    Условия: {context.user_data['conditions']}
    Контакты: {context.user_data['contacts']}
    """

    # Публикация в канал
    CHANNEL_ID = "@zarabotoknaplyazhe"  # Укажите ваш ID канала
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"Вакансия опубликована:\n{job_post}"
    )

    # Подтверждение публикации пользователю
    await update.message.reply_text("Вакансия успешно опубликована!")
    return ConversationHandler.END


# Отмена публикации
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Публикация вакансии отменена.")
    return ConversationHandler.END


# Основная функция запуска бота
def main() -> None:
    app = ApplicationBuilder().token("8067972190:AAFMXMC7_Ki6YDml4UYJMsMJUu9DwQIU4fc").build()

    # Создание обработчика диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_company)],
            REQUIREMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_requirements)],
            CONDITIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_conditions)],
            CONTACTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_contacts)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)

    app.run_polling()  # Метод run_polling не является асинхронным


if __name__ == '__main__':
    main()
