from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car
from keyboards import get_back_keyboard, get_confirm_keyboard
from states import ADDING_DRIVER, ADDING_LOGIST, ADDING_CAR

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