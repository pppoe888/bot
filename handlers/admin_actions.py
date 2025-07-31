from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car
from keyboards import get_back_keyboard, get_confirm_keyboard
from states import ADDING_DRIVER, ADDING_LOGIST, ADDING_CAR

async def handle_add_driver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса добавления водителя"""
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text="👤 Добавление водителя\n\nВведите имя водителя:",
        reply_markup=None
    )
    context.user_data["state"] = ADDING_DRIVER
    context.user_data["admin_action"] = "adding_driver"
    context.user_data["driver_data"] = {}

async def handle_add_logist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса добавления логиста"""
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text="📋 Добавление логиста\n\nВведите имя логиста:",
        reply_markup=None
    )
    context.user_data["state"] = ADDING_LOGIST
    context.user_data["admin_action"] = "adding_logist"
    context.user_data["logist_data"] = {}

async def handle_add_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса добавления машины"""
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text="🚗 Добавление машины\n\nВведите номер машины:",
        reply_markup=None
    )
    context.user_data["state"] = ADDING_CAR
    context.user_data["admin_action"] = "adding_car"
    context.user_data["car_data"] = {}

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений от админа"""
    state = context.user_data.get("state")
    text = update.message.text

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

    if state == ADDING_DRIVER:
        await handle_driver_input(update, context, text)
    elif state == ADDING_LOGIST:
        await handle_logist_input(update, context, text)
    elif state == ADDING_CAR:
        await handle_car_input(update, context, text)

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
            text="🚗 Введите модель машины (или отправьте любой текст для пропуска):",
            reply_markup=get_back_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    elif "model" not in car_data:
        car_data["model"] = text
        context.user_data["car_data"] = car_data

        # Показываем данные для подтверждения
        confirm_text = f"✅ Подтвердите данные машины:\n\n"
        confirm_text += f"🚗 Номер: {car_data['number']}\n"
        confirm_text += f"🏷️ Модель: {car_data['model']}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=confirm_text,
            reply_markup=get_confirm_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id