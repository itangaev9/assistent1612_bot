import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes

# Загружаем токен из .env
load_dotenv()
TOKEN = "7628985380:AAGzyblkfL_QMmvY8L9jm_XiODajRm10xvU"
# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Состояния для анкеты (этапы разговора)
NAME, PHONE, REQUEST = range(3)

# 🔽 СЮДА ВСТАВЬТЕ ID МЕНЕДЖЕРА (узнайте через @userinfobot в Telegram)
MANAGER_CHAT_ID = 8335114889

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! 👋\n"
        "Как я могу к вам обращаться?"
    )
    return NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"Отлично, {context.user_data['name']}!\n"
        "Укажите ваш номер телефона:"
    )
    return PHONE

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "Спасибо! Опишите суть вашего запроса:"
    )
    return REQUEST

async def finalize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['request'] = update.message.text

    lead = (
        f"📩 НОВАЯ ЗАЯВКА!\n"
        f"Имя: {context.user_data['name']}\n"
        f"Телефон: {context.user_data['phone']}\n"
        f"Запрос: {context.user_data['request']}"
    )

    await context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=lead)
    await update.message.reply_text(
        f"{context.user_data['name']}, ваша заявка принята! ✅\n"
        "Менеджер свяжется с вами в ближайшее время."
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог отменен. Для начала напишите /start.")
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, finalize)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(conv_handler)
    print("Бот запущен и слушает сообщения...")
    application.run_polling()