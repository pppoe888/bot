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
            text = "🛠️ Админ панель\n\nВыберите действие:"
            keyboard = get_admin_inline_keyboard()

            if update.callback_query:
                await update.callback_query.answer()
                try:
                    await update.callback_query.edit_message_text(text, reply_markup=keyboard)
                except Exception as e:
                    if "Message is not modified" in str(e):
                        # Сообщение уже показывает нужный контент
                        pass
                    else:
                        # Отправляем новое сообщение при ошибке
                        await update.callback_query.message.reply_text(text, reply_markup=keyboard)
            else:
                # Удаляем предыдущие сообщения
                try:
                    if context.user_data.get("last_message_id"):
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=context.user_data["last_message_id"]
                        )
                    await update.message.delete()
                except:
                    pass

                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    reply_markup=keyboard
                )
                context.user_data["last_message_id"] = message.message_id
        else:
            # Возвращаемся к главной админ панели если неизвестная команда
            text = "🛠️ Админ панель\n\nВыберите действие:"
            keyboard = get_admin_inline_keyboard()

            if update.callback_query:
                await update.callback_query.answer()
                try:
                    await update.callback_query.edit_message_text(text, reply_markup=keyboard)
                except Exception as e:
                    if "Message is not modified" in str(e):
                        # Сообщение уже показывает нужный контент
                        pass
                    else:
                        # Отправляем новое сообщение при ошибке
                        await update.callback_query.message.reply_text(text, reply_markup=keyboard)
            else:
                # Удаляем предыдущие сообщения
                try:
                    if context.user_data.get("last_message_id"):
                        await context.bot.delete_message(
                            chat_id=update.effective_chat.id,
                            message_id=context.user_data["last_message_id"]
                        )
                    await update.message.delete()
                except:
                    pass

                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    reply_markup=keyboard
                )
                context.user_data["last_message_id"] = message.message_id
    else:
            # Обычное сообщение
            text = "🛠️ Админ панель\n\nВыберите действие:"
            keyboard = get_admin_inline_keyboard()

            if update.callback_query:
                await update.callback_query.answer()
                try:
                    await update.callback_query.edit_message_text(text, reply_markup=keyboard)
                except Exception as e:
                    if "Message is not modified" in str(e):
                        # Сообщение уже показывает нужный контент
                        pass
                    else:
                        # Отправляем новое сообщение при ошибке
                        await update.callback_query.message.reply_text(text, reply_markup=keyboard)
            else:
                # Удаляем предыдущие сообщения
                await delete_previous_messages(update, context)

                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    reply_markup=keyboard
                )
                context.user_data["last_message_id"] = message.message_id

async def manage_drivers(update, context):
    await show_drivers_management(update, context)

async def manage_cars(update, context):
    await show_cars_management(update, context)

async def show_drivers_management(update, context):
    """Показать управление водителями"""
    db = SessionLocal()
    drivers = db.query(User).filter(User.role == "driver").all()
    db.close()

    text = "👥 Управление водителями:\n\n"
    if drivers:
        for driver in drivers:
            status = "✅ Авторизован" if driver.telegram_id else "❌ Не авторизован"
            text += f"• {driver.name} ({driver.phone}) - {status}\n"
    else:
        text += "Водители не найдены"

    keyboard = [
        [InlineKeyboardButton("➕ Добавить водителя", callback_data="add_driver")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
    except Exception as e:
        if "Message is not modified" in str(e):
            # Если сообщение не изменилось, просто отвечаем на callback
            await update.callback_query.answer()
        else:
            # Для других ошибок отправляем новое сообщение
            await update.callback_query.message.reply_text(
                text=text,
                reply_markup=reply_markup
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
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("👤 Введите имя водителя:")
    context.user_data["admin_action"] = "adding_driver"
    context.user_data["driver_data"] = {}

async def add_car_start(update, context):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("🚗 Введите номер машины:")
    context.user_data["admin_action"] = "adding_car"
    context.user_data["car_data"] = {}

async def delete_previous_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )
        if update.message:
            await update.message.delete()
    except Exception as e:
        print(f"Error deleting messages: {e}")