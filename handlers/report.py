
from telegram import Update
from telegram.ext import ContextTypes

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отчет смен"""
    await update.message.reply_text("📊 Отчёт смен (функция в разработке)")
