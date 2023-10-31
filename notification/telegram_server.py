import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to the Library Service API!",
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=update.message.text,
    )


if __name__ == '__main__':
    application = (
        ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    )
    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    application.run_polling()
