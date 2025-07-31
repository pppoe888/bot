
from telegram import Update
from telegram.ext import ContextTypes

async def delivery_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список доставки"""
    await update.message.reply_text("📦 Список доставки (функция в разработке)")
