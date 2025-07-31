from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car
from keyboards import get_back_keyboard, get_confirm_keyboard, get_admin_menu

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

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений в админке"""
    admin_action = context.user_data.get("admin_action")
    text = update.message.text

    # Проверяем, нажал ли пользователь кнопку "Назад"
    if text == "⬅️ Назад":
        from main import handle_back_button
        await handle_back_button(update, context)
        return

    await delete_previous_messages(update, context)

    if admin_action == "adding_driver":
        await handle_driver_input(update, context, text)
    elif admin_action == "adding_logist":
        await handle_logist_input(update, context, text)
    elif admin_action == "adding_car":
        await handle_car_input(update, context, text)

async def handle_add_driver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления водителя"""
    await update.callback_query.answer()

    context.user_data["admin_action"] = "adding_driver"
    context.user_data["driver_data"] = {}

    message = await update.callback_query.message.reply_text(
        "👤 Введите имя водителя:",
        reply_markup=get_back_keyboard()
    )
    context.user_data["last_message_id"] = message.message_id

async def handle_add_logist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления логиста"""
    await update.callback_query.answer()

    context.user_data["admin_action"] = "adding_logist"
    context.user_data["logist_data"] = {}

    message = await update.callback_query.message.reply_text(
        "👤 Введите имя логиста:",
        reply_markup=get_back_keyboard()
    )
    context.user_data["last_message_id"] = message.message_id

async def handle_add_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления машины"""
    await update.callback_query.answer()

    context.user_data["admin_action"] = "adding_car"
    context.user_data["car_data"] = {}

    message = await update.callback_query.message.reply_text(
        "🚗 Введите номер машины:",
        reply_markup=get_back_keyboard()
    )
    context.user_data["last_message_id"] = message.message_id

async def handle_driver_input(update, context, text):
    """Обработка ввода данных водителя"""
    driver_data = context.user_data.get("driver_data", {})

    if "name" not in driver_data:
        driver_data["name"] = text
        context.user_data["driver_data"] = driver_data

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📱 Введите номер телефона водителя:",
            reply_markup=get_back_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    elif "phone" not in driver_data:
        driver_data["phone"] = text
        context.user_data["driver_data"] = driver_data

        # Показываем данные для подтверждения
        confirm_text = f"✅ Подтвердите данные водителя:\n\n"
        confirm_text += f"👤 Имя: {driver_data['name']}\n"
        confirm_text += f"📱 Телефон: {driver_data['phone']}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=confirm_text,
            reply_markup=get_confirm_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

async def handle_logist_input(update, context, text):
    """Обработка ввода данных логиста"""
    logist_data = context.user_data.get("logist_data", {})

    if "name" not in logist_data:
        logist_data["name"] = text
        context.user_data["logist_data"] = logist_data

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📱 Введите номер телефона логиста:",
            reply_markup=get_back_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    elif "phone" not in logist_data:
        logist_data["phone"] = text
        context.user_data["logist_data"] = logist_data

        # Показываем данные для подтверждения
        confirm_text = f"✅ Подтвердите данные логиста:\n\n"
        confirm_text += f"👤 Имя: {logist_data['name']}\n"
        confirm_text += f"📱 Телефон: {logist_data['phone']}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=confirm_text,
            reply_markup=get_confirm_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

async def handle_car_input(update, context, text):
    """Обработка ввода данных машины"""
    car_data = context.user_data.get("car_data", {})

    if "number" not in car_data:
        car_data["number"] = text
        context.user_data["car_data"] = car_data

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🏷️ Введите марку машины (или '-' чтобы пропустить):",
            reply_markup=get_back_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    elif "brand" not in car_data:
        car_data["brand"] = text if text != "-" else ""
        context.user_data["car_data"] = car_data

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🚗 Введите модель машины (или '-' чтобы пропустить):",
            reply_markup=get_back_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    elif "model" not in car_data:
        car_data["model"] = text if text != "-" else ""
        context.user_data["car_data"] = car_data

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⛽ Введите тип топлива (или '-' чтобы пропустить):",
            reply_markup=get_back_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    elif "fuel" not in car_data:
        car_data["fuel"] = text if text != "-" else ""
        context.user_data["car_data"] = car_data

        # Показываем данные для подтверждения
        confirm_text = f"✅ Подтвердите данные машины:\n\n"
        confirm_text += f"🚗 Номер: {car_data['number']}\n"
        if car_data.get('brand'):
            confirm_text += f"🏷️ Марка: {car_data['brand']}\n"
        if car_data.get('model'):
            confirm_text += f"🚗 Модель: {car_data['model']}\n"
        if car_data.get('fuel'):
            confirm_text += f"⛽ Топливо: {car_data['fuel']}\n"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=confirm_text,
            reply_markup=get_confirm_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

async def confirm_add_driver(update, context):
    """Подтверждение добавления водителя"""
    driver_data = context.user_data.get("driver_data", {})

    if not driver_data.get("name") or not driver_data.get("phone"):
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Не все данные введены"
        )
        context.user_data["last_message_id"] = message.message_id
        return

    db = SessionLocal()
    try:
        new_driver = User(
            telegram_id=0,
            name=driver_data["name"],
            phone=driver_data["phone"],
            role="driver"
        )
        db.add(new_driver)
        db.commit()

        await delete_previous_messages(update, context)

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Водитель {driver_data['name']} успешно добавлен!",
            reply_markup=get_admin_menu()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка при добавлении: {e}"
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def confirm_add_logist(update, context):
    """Подтверждение добавления логиста"""
    logist_data = context.user_data.get("logist_data", {})

    if not logist_data.get("name") or not logist_data.get("phone"):
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Не все данные введены"
        )
        context.user_data["last_message_id"] = message.message_id
        return

    db = SessionLocal()
    try:
        new_logist = User(
            telegram_id=0,
            name=logist_data["name"],
            phone=logist_data["phone"],
            role="logist"
        )
        db.add(new_logist)
        db.commit()

        await delete_previous_messages(update, context)

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Логист {logist_data['name']} успешно добавлен!",
            reply_markup=get_admin_menu()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка при добавлении: {e}"
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def confirm_add_car(update, context):
    """Подтверждение добавления машины"""
    car_data = context.user_data.get("car_data", {})

    if not car_data.get("number"):
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Номер машины не введен"
        )
        context.user_data["last_message_id"] = message.message_id
        return

    db = SessionLocal()
    try:
        new_car = Car(
            number=car_data["number"],
            brand=car_data.get("brand", ""),
            model=car_data.get("model", ""),
            fuel=car_data.get("fuel", "")
        )
        db.add(new_car)
        db.commit()

        await delete_previous_messages(update, context)

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Машина {car_data['number']} успешно добавлена!",
            reply_markup=get_admin_menu()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка при добавлении: {e}"
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def handle_confirm(update, context):
    """Универсальный обработчик подтверждения"""
    admin_action = context.user_data.get("admin_action")

    if admin_action == "adding_driver":
        await confirm_add_driver(update, context)
    elif admin_action == "adding_logist":
        await confirm_add_logist(update, context)
    elif admin_action == "adding_car":
        await confirm_add_car(update, context)