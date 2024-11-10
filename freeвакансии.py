<<<<<<< HEAD
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)
from dotenv import load_dotenv
import nest_asyncio
import asyncio

# Загрузка токена из .env файла
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Этапы сценария
COMPANY_NAME, COMPANY_DESCRIPTION, COMPANY_WEBSITE = range(3)

# Запрещенные слова
BANNED_WORDS = ['казино', '18+', 'порно', 'эротика', 'нецензурные слова']


# Клавиатуры
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Опубликовать вакансию", callback_data='post_job')],
        [InlineKeyboardButton("Перезапустить", callback_data='restart')],
        [InlineKeyboardButton("Помощь", callback_data='help')]
    ])


def start_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Старт", callback_data='start')]])


def back_button_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]])


def help_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Сообщить о проблеме", url='https://t.me/Chessvord')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ])


# Функция старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать! Нажмите 'Старт', чтобы продолжить.",
        reply_markup=start_keyboard()
    )


# Обработчик нажатия на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'start':
        await query.message.reply_text(
            "Добрый день! Вас приветствует бот для вакансий \"Заработок на пляже💸💸💸 Вакансии бесплатно\".\n"
            "Я могу публиковать вакансии на канал. Что вы желаете?",
            reply_markup=main_menu_keyboard()
        )

    elif query.data == 'post_job':
        job_example = """
📢 Пример вакансии:

**Название компании**: ООО «Кранекс-Клаб»
📍 **Город**: Москва
💼 **Должность**: стоматолог-терапевт
💰 **Зарплата**: от 100 000 руб. в месяц
🕒 **График работы**: полный рабочий день
📅 **Требуемый опыт**: от 3 лет
📋 **Обязанности**:
- Проведение консультаций и лечение пациентов
- Ведение медицинской документации

📧 **Контакты для связи**: hr@kranex-club.ru

Лимит текста вакансии — 2000 символов.
"""
        await query.message.reply_text(job_example)
        await query.message.reply_text("Введите название компании:", reply_markup=back_button_keyboard())
        return COMPANY_NAME

    elif query.data == 'help':
        help_text = """
Правила публикации вакансий:
1. Нельзя использовать нецензурные выражения.
2. Запрещены ссылки на казино и сайты 18+.
3. Лимит текста — 2000 символов.

Если у вас возникли проблемы, нажмите на кнопку ниже.
"""
        await query.message.reply_text(help_text, reply_markup=help_menu_keyboard())

    elif query.data == 'restart':
        await query.message.reply_text("Бот перезапущен.", reply_markup=main_menu_keyboard())

    elif query.data == 'back':
        await query.message.reply_text("Что вы желаете?", reply_markup=main_menu_keyboard())
        return ConversationHandler.END


# Обработчик для ввода названия компании
async def company_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    company_name = update.message.text
    context.user_data['company_name'] = company_name
    await update.message.reply_text("Введите описание компании:", reply_markup=back_button_keyboard())
    return COMPANY_DESCRIPTION


# Обработчик для ввода описания компании
async def company_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    context.user_data['description'] = description
    await update.message.reply_text("Введите ссылку на сайт компании или напишите 'пропустить':",
                                    reply_markup=back_button_keyboard())
    return COMPANY_WEBSITE


# Обработчик для ввода ссылки на сайт
async def company_website_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    website = update.message.text

    if any(word in website.lower() for word in BANNED_WORDS):
        await update.message.reply_text(
            "Ваша заявка не принята, так как она не соответствует правилам бота.",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END

    context.user_data['website'] = website
    await update.message.reply_text("Ссылка успешно принята и опубликована на канале.")
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"Новая вакансия от {context.user_data['company_name']}!\n"
             f"Описание: {context.user_data['description']}\n"
             f"Сайт: {website if website.lower() != 'пропустить' else 'Не указан'}"
    )
    return ConversationHandler.END


# Основная функция
async def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            COMPANY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_name_handler)],
            COMPANY_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_description_handler)],
            COMPANY_WEBSITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_website_handler)],
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CommandHandler("start", start))

    await application.run_polling()


if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
=======
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

