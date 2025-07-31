from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car
from keyboards import get_admin_inline_keyboard

async def handle_add_driver(update, context):
    """Начало добавления водителя"""
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("👤 Введите имя водителя:")
    context.user_data["admin_action"] = "adding_driver"
    context.user_data["driver_data"] = {}

async def handle_add_car(update, context):
    """Начало добавления машины"""
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("🚗 Введите номер машины:")
    context.user_data["admin_action"] = "adding_car"
    context.user_data["car_data"] = {}

async def delete_previous_messages(update, context):
    """Удаляет предыдущие сообщения для очистки чата"""
    try:
        # Удаляем последнее сохраненное сообщение бота
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )
        
        # Удаляем сообщение пользователя
        if update.message:
            await update.message.delete()
        
        # Удаляем несколько предыдущих сообщений (последние 5)
        message_ids_to_delete = context.user_data.get("message_history", [])
        for msg_id in message_ids_to_delete[-5:]:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=msg_id
                )
            except:
                continue
        
        # Очищаем историю сообщений
        context.user_data["message_history"] = []
        
    except Exception as e:
        # Если не удается удалить, просто продолжаем
        pass

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений для админских действий"""
    admin_action = context.user_data.get("admin_action")

    if admin_action == "adding_driver":
        await handle_driver_adding(update, context)
    elif admin_action == "adding_car":
        await handle_car_adding(update, context)

async def handle_driver_adding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка добавления водителя по шагам"""
    from keyboards import get_confirmation_keyboard, get_back_keyboard

    driver_data = context.user_data.get("driver_data", {})
    text = update.message.text

    # Удаляем предыдущее сообщение
    try:
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )
        await update.message.delete()
    except:
        pass

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

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📋 Проверьте данные водителя:\n\n"
            f"👤 Имя: {driver_data['name']}\n"
            f"📱 Телефон: {driver_data['phone']}\n\n"
            f"Подтвердить добавление?",
            reply_markup=get_confirmation_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

async def handle_car_adding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка добавления машины по шагам"""
    from keyboards import get_confirmation_keyboard, get_back_keyboard

    car_data = context.user_data.get("car_data", {})
    text = update.message.text

    # Удаляем предыдущее сообщение
    try:
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )
        await update.message.delete()
    except:
        pass

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

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📋 Проверьте данные машины:\n\n"
            f"🚗 Номер: {car_data['number']}\n"
            f"🏷️ Модель: {car_data['model']}\n\n"
            f"Подтвердить добавление?",
            reply_markup=get_confirmation_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id