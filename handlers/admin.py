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



# === НОВЫЕ РАЗДЕЛЫ АДМИНКИ ===

async def admin_cars_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Раздел автомобили"""
    from keyboards import get_admin_cars_keyboard
    
    text = "🚗 Раздел: Автомобили\n\nВыберите действие:"
    
    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_admin_cars_keyboard()
        )
    except:
        message = await update.callback_query.message.reply_text(
            text=text,
            reply_markup=get_admin_cars_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    await update.callback_query.answer()

async def admin_employees_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Раздел сотрудники"""
    from keyboards import get_admin_employees_keyboard
    
    text = "👥 Раздел: Сотрудники\n\nВыберите действие:"
    
    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_admin_employees_keyboard()
        )
    except:
        message = await update.callback_query.message.reply_text(
            text=text,
            reply_markup=get_admin_employees_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    await update.callback_query.answer()

async def admin_shifts_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Раздел смены"""
    from keyboards import get_admin_shifts_keyboard
    
    text = "🚛 Раздел: Смены\n\nВыберите действие:"
    
    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_admin_shifts_keyboard()
        )
    except:
        message = await update.callback_query.message.reply_text(
            text=text,
            reply_markup=get_admin_shifts_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    await update.callback_query.answer()

async def admin_reports_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Раздел отчеты"""
    from keyboards import get_admin_reports_keyboard
    
    text = "📊 Раздел: Отчеты\n\nВыберите тип отчета:"
    
    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_admin_reports_keyboard()
        )
    except:
        message = await update.callback_query.message.reply_text(
            text=text,
            reply_markup=get_admin_reports_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    await update.callback_query.answer()

async def cars_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика по машинам"""
    from keyboards import get_admin_cars_keyboard
    
    db = SessionLocal()
    try:
        cars_count = db.query(Car).count()
        active_cars = db.query(Shift).filter(Shift.is_active == True).count()
        
        text = "📊 Статистика по автомобилям\n\n"
        text += f"🚗 Всего машин: {cars_count}\n"
        text += f"🚛 В работе: {active_cars}\n"
        text += f"🅿️ Свободно: {cars_count - active_cars}"

        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=get_admin_cars_keyboard()
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=get_admin_cars_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await update.callback_query.answer()

async def employees_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика по сотрудникам"""
    from keyboards import get_admin_employees_keyboard
    
    db = SessionLocal()
    try:
        drivers_count = db.query(User).filter(User.role == "driver").count()
        logists_count = db.query(User).filter(User.role == "logist").count()
        active_drivers = db.query(Shift).filter(Shift.is_active == True).count()
        
        text = "📊 Статистика по сотрудникам\n\n"
        text += f"👤 Всего водителей: {drivers_count}\n"
        text += f"🚛 На смене: {active_drivers}\n"
        text += f"📋 Логистов: {logists_count}"

        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=get_admin_employees_keyboard()
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=get_admin_employees_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await update.callback_query.answer()

async def shifts_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика по сменам"""
    from keyboards import get_admin_shifts_keyboard
    
    db = SessionLocal()
    try:
        active_shifts = db.query(Shift).filter(Shift.is_active == True).count()
        total_shifts = db.query(Shift).count()
        completed_shifts = total_shifts - active_shifts
        
        text = "📊 Статистика по сменам\n\n"
        text += f"🚛 Активных смен: {active_shifts}\n"
        text += f"✅ Завершенных смен: {completed_shifts}\n"
        text += f"📈 Всего смен: {total_shifts}"

        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=get_admin_shifts_keyboard()
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=get_admin_shifts_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await update.callback_query.answer()