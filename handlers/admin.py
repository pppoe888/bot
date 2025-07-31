from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car, Shift
from keyboards import get_admin_inline_keyboard, get_manage_drivers_keyboard, get_manage_logists_keyboard, get_manage_cars_keyboard

async def delete_previous_messages(update, context):
    """Удаляет предыдущие сообщения"""
    try:
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")

    try:
        if update.message:
            await update.message.delete()
    except Exception as e:
        print(f"Ошибка при удалении текущего сообщения: {e}")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ панель"""
    text = "👑 Админ панель\n\nВыберите действие:"

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

    await update.callback_query.answer()

async def manage_drivers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Управление водителями"""
    db = SessionLocal()
    try:
        drivers = db.query(User).filter(User.role == "driver").all()

        text = "👤 Управление водителями\n\n"
        if drivers:
            for driver in drivers:
                text += f"• {driver.name} ({driver.phone})\n"
        else:
            text += "Водители не найдены."

        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=get_manage_drivers_keyboard()
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=get_manage_drivers_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id

    finally:
        db.close()

    await update.callback_query.answer()

async def manage_cars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Управление машинами"""
    db = SessionLocal()
    try:
        cars = db.query(Car).all()

        text = "🚗 Управление машинами\n\n"
        if cars:
            for car in cars:
                text += f"• {car.number}"
                if car.brand:
                    text += f" ({car.brand}"
                    if car.model:
                        text += f" {car.model}"
                    text += ")"
                text += "\n"
        else:
            text += "Машины не найдены."

        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=get_manage_cars_keyboard()
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=get_manage_cars_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id

    finally:
        db.close()

    await update.callback_query.answer()

async def manage_logists(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Управление логистами"""
    db = SessionLocal()
    try:
        logists = db.query(User).filter(User.role == "logist").all()

        text = "📋 Управление логистами\n\n"
        if logists:
            for logist in logists:
                text += f"• {logist.name} ({logist.phone})\n"
        else:
            text += "Логисты не найдены."

        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=get_manage_logists_keyboard()
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=get_manage_logists_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id

    finally:
        db.close()

    await update.callback_query.answer()

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика"""
    db = SessionLocal()
    try:
        drivers_count = db.query(User).filter(User.role == "driver").count()
        logists_count = db.query(User).filter(User.role == "logist").count()
        cars_count = db.query(Car).count()
        active_shifts = db.query(Shift).filter(Shift.is_active == True).count()

        text = "📊 Статистика\n\n"
        text += f"👤 Водители: {drivers_count}\n"
        text += f"📋 Логисты: {logists_count}\n"
        text += f"🚗 Машины: {cars_count}\n"
        text += f"🚛 Активные смены: {active_shifts}"

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

    await update.callback_query.answer()

async def admin_panel_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ панель для текстовых сообщений"""
    await delete_previous_messages(update, context)

    text = "👑 Админ панель\n\nВыберите действие:"
    message = await update.message.reply_text(
        text=text,
        reply_markup=get_admin_inline_keyboard()
    )
    context.user_data["last_message_id"] = message.message_id

async def manage_cars_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Управление машинами для текстовых сообщений"""
    await delete_previous_messages(update, context)

    db = SessionLocal()
    try:
        cars = db.query(Car).all()

        text = "🚗 Управление машинами\n\n"
        if cars:
            for car in cars:
                text += f"• {car.number}"
                if car.brand:
                    text += f" ({car.brand}"
                    if car.model:
                        text += f" {car.model}"
                    text += ")"
                text += "\n"
        else:
            text += "Машины не найдены."

        message = await update.message.reply_text(
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def admin_stats_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика для текстовых сообщений"""
    await delete_previous_messages(update, context)

    db = SessionLocal()
    try:
        drivers_count = db.query(User).filter(User.role == "driver").count()
        logists_count = db.query(User).filter(User.role == "logist").count()
        cars_count = db.query(Car).count()

        text = "📊 Статистика\n\n"
        text += f"👤 Водители: {drivers_count}\n"
        text += f"📋 Логисты: {logists_count}\n"
        text += f"🚗 Машины: {cars_count}"

        message = await update.message.reply_text(
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()