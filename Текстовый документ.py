from telegram import Update, LabeledPrice
from telegram.ext import Application, CommandHandler, MessageHandler, filters, PreCheckoutQueryHandler, CallbackContext

# Стоимости вакансий по профессиям
job_prices = {
    "копирайтер": 20000,  # 200 рублей
    "дизайнер": 30000,    # 300 рублей
    "видеомонтаж": 40000, # 400 рублей
    "программист": 50000   # 500 рублей
}

# Функция для старта
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Используйте /add_vacancy для подачи вакансии.')

# Функция для добавления вакансии
async def add_vacancy(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Введите название вакансии:')
    context.user_data['step'] = 'title'  # Сохраняем текущий шаг

# Функция для обработки сообщений по шагам
async def handle_message(update: Update, context: CallbackContext) -> None:
    step = context.user_data.get('step')

    if step == 'title':
        title = update.message.text
        if len(title) < 3:
            await update.message.reply_text('Название вакансии должно быть больше 3 символов. Введите название ещё раз:')
        else:
            context.user_data['title'] = title
            await update.message.reply_text('Введите описание вакансии:')
            context.user_data['step'] = 'description'

    elif step == 'description':
        description = update.message.text
        if len(description) < 10:
            await update.message.reply_text('Описание вакансии должно быть больше 10 символов. Введите описание ещё раз:')
        else:
            context.user_data['description'] = description
            await update.message.reply_text('Введите условия работы:')
            context.user_data['step'] = 'conditions'

    elif step == 'conditions':
        conditions = update.message.text
        if len(conditions) < 5:
            await update.message.reply_text('Условия работы должны быть чёткими. Введите условия ещё раз:')
        else:
            context.user_data['conditions'] = conditions
            await update.message.reply_text('Введите профессию (копирайтер, дизайнер, видеомонтаж, программист):')
            context.user_data['step'] = 'salary'

    elif step == 'salary':
        job_title = update.message.text.lower()
        if job_title not in job_prices:
            await update.message.reply_text('Неверная профессия. Введите одну из следующих: копирайтер, дизайнер, видеомонтаж, программист.')
        else:
            context.user_data['salary'] = job_prices[job_title]
            await update.message.reply_text('Ваша вакансия:\n'
                                            f"Название: {context.user_data['title']}\n"
                                            f"Описание: {context.user_data['description']}\n"
                                            f"Условия: {context.user_data['conditions']}\n"
                                            f"Зарплата: {context.user_data['salary'] // 100:.2f} рублей\n"
                                            "Подтверждаете? (Да/Нет)")
            context.user_data['step'] = 'confirm'

# Функция для подтверждения публикации вакансии
async def confirm_vacancy(update: Update, context: CallbackContext) -> None:
    if update.message.text.lower() == 'да':
        await send_invoice(update, context)
    else:
        await update.message.reply_text('Вакансия не была опубликована.')

# Функция для отправки инвойса
async def send_invoice(update: Update, context: CallbackContext) -> None:
    title = "Оплата за публикацию вакансии"
    description = f"Оплата за размещение вакансии '{context.user_data['title']}'"
    payload = "custom-payload"
    currency = "RUB"
    price = context.user_data['salary']
    prices = [LabeledPrice("Публикация вакансии", price)]

    await context.bot.send_invoice(
        chat_id=update.message.chat.id,
        title=title,
        description=description,
        payload=payload,
        provider_token="YOUR_PROVIDER_TOKEN",  # Токен платежного провайдера
        currency=currency,
        prices=prices,
        start_parameter="payment",
        is_flexible=False
    )

# Функция для обработки предоплаты
async def precheckout_callback(update: Update, context: CallbackContext) -> None:
    query = update.pre_checkout_query
    await query.answer(ok=(query.invoice_payload == 'custom-payload'))

# Функция для обработки успешной оплаты
async def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Оплата прошла успешно! Вакансия опубликована.')
    await context.bot.send_message(
        chat_id='YOUR_CHANNEL_ID',  # Замените на ID вашего канала
        text=f"Новая вакансия:\n"
             f"Название: {context.user_data['title']}\n"
             f"Описание: {context.user_data['description']}\n"
             f"Условия: {context.user_data['conditions']}\n"
             f"Зарплата: {context.user_data['salary'] // 100:.2f} рублей\n"
    )

# Основная функция
async def main() -> None:
    application = Application.builder().token("YOUR_TOKEN").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_vacancy", add_vacancy))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Regex('^(Да|Нет)$'), confirm_vacancy))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    await application.start()
    await application.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
