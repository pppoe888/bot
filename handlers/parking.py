
from telegram import Update
from telegram.ext import ContextTypes

async def parking_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка стоянки"""
    await update.message.reply_text("🅿️ Стоянка (функция в разработке)")
