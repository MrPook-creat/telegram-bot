import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
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
        await query.message.reply_text("Введите название компании:")
        return COMPANY_NAME
    elif query.data == 'help':
        await query.message.reply_text("Правила публикации вакансий...")
    elif query.data == 'restart':
        await query.message.reply_text("Бот перезапущен.", reply_markup=main_menu_keyboard())

async def company_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    company_name = update.message.text
    context.user_data['company_name'] = company_name
    await update.message.reply_text("Введите описание компании:")
    return COMPANY_DESCRIPTION

async def company_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    context.user_data['description'] = description
    await update.message.reply_text("Введите ссылку на сайт компании:")
    return COMPANY_WEBSITE

async def company_website_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    website = update.message.text
    context.user_data['website'] = website

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

    await update.message.reply_text("Вакансия успешно опубликована!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Публикация вакансии отменена.")
    return ConversationHandler.END

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

# Фиктивный веб-сервер для Render
async def handle(request):
    return web.Response(text="Бот работает!")

async def run_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    port = int(os.getenv("PORT", 5000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Сервер запущен на порту {port}")

if __name__ == "__main__":
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.create_task(run_telegram_bot())
    loop.run_until_complete(run_web_server())
