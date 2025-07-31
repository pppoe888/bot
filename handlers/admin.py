from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car, Shift
from config import ADMIN_ID
from keyboards import get_admin_inline_keyboard, get_manage_drivers_keyboard, get_manage_cars_keyboard, get_manage_logists_keyboard

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ панель"""
    # Проверка что пользователь - настоящий админ
    if update.effective_user.id != ADMIN_ID:
        if update.callback_query:
            await update.callback_query.answer("❌ У вас нет прав администратора.")
        else:
            await update.message.reply_text("❌ У вас нет прав администратора.")
        return

    try:
        # Удаляем предыдущие сообщения
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )

        if update.message:
            await update.message.delete()
    except:
        pass

    text = "🛠️ Админ панель\n\nВыберите действие:"
    keyboard = get_admin_inline_keyboard()

    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=keyboard
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=keyboard
            )
            context.user_data["last_message_id"] = message.message_id
        await update.callback_query.answer()
    else:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=keyboard
        )
        context.user_data["last_message_id"] = message.message_id

async def manage_drivers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Управление водителями"""
    await update.callback_query.answer()

    text = "👥 Управление водителями\n\nВыберите действие:"
    keyboard = get_manage_drivers_keyboard()

    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard
        )
    except:
        message = await update.callback_query.message.reply_text(
            text=text,
            reply_markup=keyboard
        )
        context.user_data["last_message_id"] = message.message_id

async def manage_cars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Управление машинами"""
    await update.callback_query.answer()

    text = "🚗 Управление машинами\n\nВыберите действие:"
    keyboard = get_manage_cars_keyboard()

    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard
        )
    except:
        message = await update.callback_query.message.reply_text(
            text=text,
            reply_markup=keyboard
        )
        context.user_data["last_message_id"] = message.message_id

async def manage_logists(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Управление логистами"""
    await update.callback_query.answer()

    text = "📋 Управление логистами\n\nВыберите действие:"
    keyboard = get_manage_logists_keyboard()

    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard
        )
    except:
        message = await update.callback_query.message.reply_text(
            text=text,
            reply_markup=keyboard
        )
        context.user_data["last_message_id"] = message.message_id

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика админа"""
    await update.callback_query.answer()

    db = SessionLocal()
    try:
        drivers_count = db.query(User).filter(User.role == "driver").count()
        logists_count = db.query(User).filter(User.role == "logist").count()
        cars_count = db.query(Car).count()
        active_shifts = db.query(Shift).filter(Shift.end_time.is_(None)).count()
    finally:
        db.close()

    text = f"📊 Статистика системы\n\n"
    text += f"👥 Водителей: {drivers_count}\n"
    text += f"📋 Логистов: {logists_count}\n"
    text += f"🚗 Машин: {cars_count}\n"
    text += f"🚛 Активных смен: {active_shifts}\n"

    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel")]
    ]

    try:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        if "Message is not modified" in str(e):
            await update.callback_query.answer()
        else:
            await update.callback_query.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )