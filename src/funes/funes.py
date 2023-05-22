#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position

import logging
import os

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()


from .chat import chat

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

app = FastAPI()
token = os.environ['TELEGRAM_BOT_TOKEN']
bot = Application.builder().token(token).build()


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(f"Enter '{update.message.text} help' for help")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    logger.info(f"Message incoming: {update}")
    reply = await chat(update.message.from_user.id, update.message.text)
    await update.message.reply_text(reply)


@app.on_event('startup')
async def run_bot() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.


    # on different commands - answer in Telegram
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    await bot.initialize()
    await bot.updater.start_polling()
    await bot.start()


@app.on_event('shutdown')
async def stop_bot() -> None:
    if bot.updater.running:  # type: ignore[union-attr]
        await bot.updater.stop()
    if bot.running:
        await bot.stop()
    await bot.shutdown()


@app.get("/")
async def root():
    return {"message": "Hello World"}

