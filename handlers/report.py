
from telegram import Update
from telegram.ext import ContextTypes

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отчёт"""
    text = "📊 Отчёт\n\n🚧 Функция в разработке"
    
    # Удаляем предыдущие сообщения
    try:
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )
        if update.message:
            await update.message.delete()
    except:
        pass
        
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )
    context.user_data["last_message_id"] = message.message_id
