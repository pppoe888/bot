
from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car
from keyboards import get_admin_inline_keyboard, get_manage_drivers_keyboard, get_manage_cars_keyboard, get_manage_logists_keyboard

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ панель"""
    await update.callback_query.answer()

    text = "🛠️ Админ панель\n\nВыберите действие:"
    keyboard = get_admin_inline_keyboard()

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

async def manage_drivers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Управление водителями"""
    await update.callback_query.answer()

    text = "🚛 Управление водителями\n\nВыберите действие:"
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
        # Получаем статистику
        drivers_count = db.query(User).filter(User.role == "driver").count()
        logists_count = db.query(User).filter(User.role == "logist").count()
        cars_count = db.query(Car).count()

        text = f"📊 Статистика системы:\n\n"
        text += f"👥 Водителей: {drivers_count}\n"
        text += f"📋 Логистов: {logists_count}\n"
        text += f"🚗 Машин: {cars_count}"

        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=get_admin_inline_keyboard()
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=get_admin_inline_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        text = f"❌ Ошибка получения статистики: {str(e)}"
        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=get_admin_inline_keyboard()
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=get_admin_inline_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()
