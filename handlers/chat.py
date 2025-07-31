
from telegram import Update
from telegram.ext import ContextTypes

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💬 Чат водителей (функционал в разработке)")
