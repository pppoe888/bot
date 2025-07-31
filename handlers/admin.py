
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car, Shift
from config import ADMIN_ID
from keyboards import get_admin_inline_keyboard

async def admin_panel(update, context):
    # Проверка что пользователь - настоящий админ
    if update.effective_user.id != ADMIN_ID:
        if update.callback_query:
            await update.callback_query.answer("❌ У вас нет прав администратора.")
        else:
            await update.message.reply_text("❌ У вас нет прав администратора.")
        return

    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == "manage_drivers":
            await show_drivers_management(update, context)
        elif query.data == "manage_cars":
            await show_cars_management(update, context)
        elif query.data == "admin_stats":
            await show_admin_stats(update, context)
        elif query.data == "add_driver":
            await add_driver_start(update, context)
        elif query.data == "add_car":
            await add_car_start(update, context)
        elif query.data == "back_to_admin":
            await query.edit_message_text(
                "🛠️ Админ панель",
                reply_markup=get_admin_inline_keyboard()
            )
        else:
            # Возвращаемся к главной админ панели если неизвестная команда
            await query.edit_message_text(
                "🛠️ Админ панель",
                reply_markup=get_admin_inline_keyboard()
            )
    else:
        # Обычное сообщение
        await update.message.reply_text(
            "🛠️ Админ панель",
            reply_markup=get_admin_inline_keyboard()
        )

async def manage_drivers(update, context):
    await show_drivers_management(update, context)

async def manage_cars(update, context):
    await show_cars_management(update, context)

async def show_drivers_management(update, context):
    db = SessionLocal()
    drivers = db.query(User).filter(User.role == "driver").all()
    db.close()

    text = "👥 Управление водителями:\n\n"
    if drivers:
        for driver in drivers:
            status = "📱 Зарегистрирован" if driver.telegram_id else "⏳ Не зарегистрирован"
            text += f"👤 {driver.name}\n📞 {driver.phone}\n{status}\n\n"
    else:
        text += "Водителей пока нет."

    keyboard = [
        [InlineKeyboardButton("➕ Добавить водителя", callback_data="add_driver")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_admin")]
    ]

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_cars_management(update, context):
    db = SessionLocal()
    cars = db.query(Car).all()
    db.close()

    text = "🚗 Управление машинами:\n\n"
    if cars:
        for car in cars:
            text += f"🚗 {car.number}\n🏭 {car.brand} {car.model}\n⛽ {car.fuel}\n📏 {car.current_mileage} км\n\n"
    else:
        text += "Машин пока нет."

    keyboard = [
        [InlineKeyboardButton("➕ Добавить машину", callback_data="add_car")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_admin")]
    ]

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_admin_stats(update, context):
    db = SessionLocal()
    drivers_count = db.query(User).filter(User.role == "driver").count()
    cars_count = db.query(Car).count()
    active_shifts = db.query(Shift).filter(Shift.status == "active").count()
    db.close()

    text = f"📊 Статистика:\n\n👥 Водителей: {drivers_count}\n🚗 Машин: {cars_count}\n🚛 Активных смен: {active_shifts}"

    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_admin")]]

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def add_driver_start(update, context):
    await update.callback_query.edit_message_text("👤 Введите имя водителя:")
    context.user_data["admin_action"] = "adding_driver"
    context.user_data["driver_data"] = {}

async def add_car_start(update, context):
    await update.callback_query.edit_message_text("🚗 Введите номер машины:")
    context.user_data["admin_action"] = "adding_car" 
    context.user_data["car_data"] = {}
