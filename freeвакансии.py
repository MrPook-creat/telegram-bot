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
from aiohttp import web

# Загрузка токена из .env файла
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Шаги сценария
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
    await update.message.reply_text("Добро пожаловать! Нажмите 'Старт', чтобы продолжить.", reply_markup=start_keyboard())

# Обработчик нажатия на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'start':
        await query.message.reply_text("Вас приветствует бот для вакансий. Что вы хотите сделать?", reply_markup=main_menu_keyboard())
    elif query.data == 'post_job':
        await query.message.reply_text("Пример вакансии: ... Введите название компании:", reply_markup=back_button_keyboard())
        return COMPANY_NAME
    elif query.data == 'help':
        await query.message.reply_text("Добро пожаловать в раздел помощи.", reply_markup=help_menu_keyboard())
    elif query.data == 'restart':
        await query.message.reply_text("Бот перезапущен.", reply_markup=main_menu_keyboard())
    elif query.data == 'back':
        await query.message.reply_text("Возвращаемся назад.", reply_markup=main_menu_keyboard())
        return ConversationHandler.END

# Функции для обработки ввода данных от пользователя (название компании, описание и т.д.)
async def company_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['company_name'] = update.message.text
    await update.message.reply_text("Введите описание компании:", reply_markup=back_button_keyboard())
    return COMPANY_DESCRIPTION

async def company_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['company_description'] = update.message.text
    await update.message.reply_text("Введите веб-сайт компании:", reply_markup=back_button_keyboard())
    return COMPANY_WEBSITE

async def company_website_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    company_name = context.user_data.get('company_name')
    company_description = context.user_data.get('company_description')
    company_website = update.message.text

    # Проверка на наличие запрещенных слов
    for word in BANNED_WORDS:
        if word in company_name.lower() or word in company_description.lower():
            await update.message.reply_text("Ваша вакансия содержит запрещенные слова!")
            return ConversationHandler.END

    # Отправка вакансии в канал
    message = f"Новая вакансия:\n\nКомпания: {company_name}\nОписание: {company_description}\nСайт: {company_website}"
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message)

    await update.message.reply_text("Вакансия опубликована!", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

# Функция обработки отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Публикация вакансии отменена.")
    return ConversationHandler.END

# Основная функция для запуска Telegram-бота
async def run_telegram_bot():
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

# Функция для обработки запроса через aiohttp
async def handle(request):
    return web.Response(text="Bot is running")

# Настройка и запуск aiohttp сервера
async def init():
    server = web.Application()
    server.router.add_get("/", handle)
    return server

# Функция для запуска обоих серверов параллельно
async def main():
    # Запуск Telegram бота в отдельном таске
    telegram_task = asyncio.create_task(run_telegram_bot())

    # Запуск aiohttp сервера
    aiohttp_app = await init()
    aiohttp_task = asyncio.create_task(web.run_app(aiohttp_app, port=int(os.environ.get("PORT", 8080))))

    # Ожидание завершения всех задач
    await asyncio.gather(telegram_task, aiohttp_task)

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(main())
