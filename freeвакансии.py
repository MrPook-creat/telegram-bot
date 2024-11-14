import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, ReplyKeyboardMarkup
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, ContextTypes, filters
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

# Шаги сценария
COMPANY_NAME, COMPANY_DESCRIPTION, COMPANY_WEBSITE = range(3)
TITLE, DESCRIPTION, COMPANY, REQUIREMENTS, CONDITIONS, CONTACTS = range(6)

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
            "Вас приветствует бот для вакансий. Что вы хотите сделать?",
            reply_markup=main_menu_keyboard()
        )
    elif query.data == 'post_job':
        await query.message.reply_text("Введите название компании:", reply_markup=back_button_keyboard())
        return COMPANY_NAME
    elif query.data == 'help':
        await query.message.reply_text(
            "Правила публикации вакансий...",
            reply_markup=help_menu_keyboard()
        )
    elif query.data == 'restart':
        await query.message.reply_text("Бот перезапущен.", reply_markup=main_menu_keyboard())
    elif query.data == 'back':
        await query.message.reply_text("Возвращаемся назад.", reply_markup=main_menu_keyboard())
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
    await update.message.reply_text("Введите ссылку на сайт компании или напишите 'пропустить':", reply_markup=back_button_keyboard())
    return COMPANY_WEBSITE

# Обработчик для ввода ссылки на сайт
async def company_website_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    website = update.message.text
    context.user_data['website'] = website if website.lower() != 'пропустить' else 'Не указан'

    if any(word in website.lower() for word in BANNED_WORDS):
        await update.message.reply_text("Ваша заявка не принята из-за запрещённых слов.")
        return ConversationHandler.END

    # Отправляем вакансию в канал
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=f"Новая вакансия от {context.user_data['company_name']}!\n"
             f"Описание: {context.user_data['description']}\n"
             f"Сайт: {context.user_data['website']}"
    )

    # Подтверждение публикации с кнопкой "Старт"
    await update.message.reply_text(
        "Вакансия успешно опубликована! Если желаете написать новую вакансию, пропишите в этом чате команду: /start или нажмите на кнопку 'Старт'.",
        reply_markup=start_keyboard()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Публикация вакансии отменена.")
    return ConversationHandler.END

# Основная функция
async def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Создание обработчика диалога
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            COMPANY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_name_handler)],
            COMPANY_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_description_handler)],
            COMPANY_WEBSITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_website_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    await application.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
