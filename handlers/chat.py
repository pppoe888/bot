from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User, ChatMessage
from keyboards import get_chat_menu, get_back_keyboard
from states import WRITING_MESSAGE
from datetime import datetime

async def delete_previous_messages(update, context):
    """Удаляет предыдущие сообщения"""
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

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главная функция чата"""
    await delete_previous_messages(update, context)

    # Проверяем авторизацию
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

        if not user:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Вы не авторизованы. Используйте /start для авторизации."
            )
            context.user_data["last_message_id"] = message.message_id
            return

        # Получаем последние 10 сообщений
        messages = db.query(ChatMessage).order_by(ChatMessage.timestamp.desc()).limit(10).all()
        messages.reverse()  # Показываем в правильном порядке

        if not messages:
            chat_text = "💬 Чат водителей\n\n📝 Сообщений пока нет."
        else:
            chat_text = "💬 Чат водителей\n\n"
            for msg in messages:
                time_str = msg.timestamp.strftime("%H:%M")
                role_emoji = "👑" if msg.user.role == "admin" else "🚛"
                chat_text += f"{role_emoji} {msg.user.name} ({time_str}):\n{msg.message}\n\n"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=chat_text,
            reply_markup=get_chat_menu()
        )
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка: {e}"
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def write_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переходит в режим написания сообщения"""
    await delete_previous_messages(update, context)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✍️ Напишите ваше сообщение:",
        reply_markup=get_back_keyboard()
    )
    context.user_data["state"] = WRITING_MESSAGE
    context.user_data["last_message_id"] = message.message_id

async def send_message_to_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет сообщение в чат"""
    if context.user_data.get("state") != WRITING_MESSAGE:
        return

    # Проверяем авторизацию
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

        if not user:
            await delete_previous_messages(update, context)
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Вы не авторизованы. Используйте /start для авторизации."
            )
            context.user_data["last_message_id"] = message.message_id
            return

        # Сохраняем сообщение в базу
        new_message = ChatMessage(
            user_id=user.id,
            message=update.message.text,
            timestamp=datetime.now()
        )

        db.add(new_message)
        db.commit()

        await delete_previous_messages(update, context)

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ Сообщение отправлено в чат!",
            reply_markup=get_chat_menu()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка: {e}"
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def refresh_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обновить чат"""
    await chat(update, context)