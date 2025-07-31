
from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User, ChatMessage
from keyboards import get_chat_keyboard
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
    """Показать чат"""
    await delete_previous_messages(update, context)

    db = SessionLocal()
    try:
        # Получаем последние 10 сообщений
        messages = db.query(ChatMessage).join(User).order_by(ChatMessage.timestamp.desc()).limit(10).all()
        
        if not messages:
            text = "💬 Чат пуст\n\nПока что никто ничего не написал."
        else:
            text = "💬 Чат водителей\n\n"
            for msg in reversed(messages):
                time_str = msg.timestamp.strftime("%H:%M")
                text += f"[{time_str}] {msg.user.name}: {msg.message}\n"
        
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_chat_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка загрузки чата: {str(e)}",
            reply_markup=get_chat_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def write_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Режим написания сообщения"""
    await delete_previous_messages(update, context)

    context.user_data["state"] = "writing_message"

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✍️ Напишите ваше сообщение:",
        reply_markup=get_chat_keyboard()
    )
    context.user_data["last_message_id"] = message.message_id

async def send_message_to_chat(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
    """Отправка сообщения в чат"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

        if not user:
            await delete_previous_messages(update, context)
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Пользователь не найден!",
                reply_markup=get_chat_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id
            return

        # Сохраняем сообщение в базу
        new_message = ChatMessage(
            user_id=user.id,
            message=message_text,
            timestamp=datetime.now()
        )

        db.add(new_message)
        db.commit()

        await delete_previous_messages(update, context)

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="✅ Сообщение отправлено в чат!",
            reply_markup=get_chat_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

        # Очищаем состояние
        context.user_data.pop("state", None)

    except Exception as e:
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка отправки сообщения: {str(e)}",
            reply_markup=get_chat_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def refresh_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обновление чата"""
    await chat(update, context)
