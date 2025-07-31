from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car
from keyboards import get_admin_menu, get_back_keyboard, get_confirm_keyboard
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
    """Обработка текста в админских состояниях"""
    text = update.message.text
    current_state = context.user_data.get("state")

    if current_state == ADDING_DRIVER:
        await handle_driver_input(update, context, text)
    elif current_state == ADDING_LOGIST:
        await handle_logist_input(update, context, text)
    elif current_state == ADDING_CAR:
        await handle_car_input(update, context, text)

async def handle_driver_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обработка ввода данных водителя"""
    step = context.user_data.get("driver_step")
    
    if step == "name":
        context.user_data["driver_data"] = {"name": text}
        context.user_data["driver_step"] = "phone"
        await update.message.reply_text("📱 Введите номер телефона водителя:")
    elif step == "phone":
        driver_data = context.user_data.get("driver_data", {})
        driver_data["phone"] = text
        context.user_data["driver_data"] = driver_data
        
        # Показываем подтверждение
        confirm_text = f"✅ Подтвердите добавление водителя:\n\n"
        confirm_text += f"👤 Имя: {driver_data['name']}\n"
        confirm_text += f"📱 Телефон: {driver_data['phone']}"
        
        await update.message.reply_text(confirm_text, reply_markup=get_confirm_keyboard())

async def handle_logist_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обработка ввода данных логиста"""
    step = context.user_data.get("logist_step")
    
    if step == "name":
        context.user_data["logist_data"] = {"name": text}
        context.user_data["logist_step"] = "phone"
        await update.message.reply_text("📱 Введите номер телефона логиста:")
    elif step == "phone":
        logist_data = context.user_data.get("logist_data", {})
        logist_data["phone"] = text
        context.user_data["logist_data"] = logist_data
        
        # Показываем подтверждение
        confirm_text = f"✅ Подтвердите добавление логиста:\n\n"
        confirm_text += f"👤 Имя: {logist_data['name']}\n"
        confirm_text += f"📱 Телефон: {logist_data['phone']}"
        
        await update.message.reply_text(confirm_text, reply_markup=get_confirm_keyboard())

async def handle_car_input(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Обработка ввода данных машины"""
    step = context.user_data.get("car_step")
    
    if step == "number":
        context.user_data["car_data"] = {"number": text}
        context.user_data["car_step"] = "brand"
        await update.message.reply_text("🚗 Введите марку машины:")
    elif step == "brand":
        car_data = context.user_data.get("car_data", {})
        car_data["brand"] = text
        context.user_data["car_data"] = car_data
        context.user_data["car_step"] = "model"
        await update.message.reply_text("🚙 Введите модель машины:")
    elif step == "model":
        car_data = context.user_data.get("car_data", {})
        car_data["model"] = text
        context.user_data["car_data"] = car_data
        
        # Показываем подтверждение
        confirm_text = f"✅ Подтвердите добавление машины:\n\n"
        confirm_text += f"🔢 Номер: {car_data['number']}\n"
        confirm_text += f"🚗 Марка: {car_data['brand']}\n"
        confirm_text += f"🚙 Модель: {car_data['model']}"
        
        await update.message.reply_text(confirm_text, reply_markup=get_confirm_keyboard())

async def handle_add_driver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать процесс добавления водителя"""
    await update.callback_query.answer()
    
    text = "👤 Добавление нового водителя\n\nВведите имя водителя:"
    
    try:
        await update.callback_query.edit_message_text(text)
    except:
        message = await update.callback_query.message.reply_text(text)
        context.user_data["last_message_id"] = message.message_id
    
    context.user_data["state"] = ADDING_DRIVER
    context.user_data["driver_step"] = "name"

async def handle_add_logist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать процесс добавления логиста"""
    await update.callback_query.answer()
    
    text = "📋 Добавление нового логиста\n\nВведите имя логиста:"
    
    try:
        await update.callback_query.edit_message_text(text)
    except:
        message = await update.callback_query.message.reply_text(text)
        context.user_data["last_message_id"] = message.message_id
    
    context.user_data["state"] = ADDING_LOGIST
    context.user_data["logist_step"] = "name" добавления водителя"""
    await delete_previous_messages(update, context)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👤 Введите имя водителя:",
        reply_markup=get_back_keyboard()
    )
    context.user_data["state"] = ADDING_DRIVER
    context.user_data["driver_data"] = {}
    context.user_data["last_message_id"] = message.message_id

    if update.callback_query:
        await update.callback_query.answer()

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

async def handle_add_logist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать процесс добавления логиста"""
    await delete_previous_messages(update, context)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👤 Введите имя логиста:",
        reply_markup=get_back_keyboard()
    )
    context.user_data["state"] = ADDING_LOGIST
    context.user_data["logist_data"] = {}
    context.user_data["last_message_id"] = message.message_id

    if update.callback_query:
        await update.callback_query.answer()

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

async def handle_add_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать процесс добавления машины"""
    await update.callback_query.answer()
    
    text = "🚗 Добавление новой машины\n\nВведите номер машины:"
    
    try:
        await update.callback_query.edit_message_text(text)
    except:
        message = await update.callback_query.message.reply_text(text)
        context.user_data["last_message_id"] = message.message_id
    
    context.user_data["state"] = ADDING_CAR
    context.user_data["car_step"] = "number" добавления машины"""
    await delete_previous_messages(update, context)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🚗 Введите номер машины:",
        reply_markup=get_back_keyboard()
    )
    context.user_data["state"] = ADDING_CAR
    context.user_data["car_data"] = {}
    context.user_data["last_message_id"] = message.message_id

    if update.callback_query:
        await update.callback_query.answer()

async def handle_car_input(update, context, text):
    """Обработка ввода данных машины"""
    car_data = context.user_data.get("car_data", {})

    if "number" not in car_data:
        car_data["number"] = text
        context.user_data["car_data"] = car_data

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🏭 Введите марку машины (или напишите 'пропустить'):",
            reply_markup=get_back_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    elif "brand" not in car_data:
        if text.lower() != "пропустить":
            car_data["brand"] = text
        else:
            car_data["brand"] = ""
        context.user_data["car_data"] = car_data

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🚙 Введите модель машины (или напишите 'пропустить'):",
            reply_markup=get_back_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    elif "model" not in car_data:
        if text.lower() != "пропустить":
            car_data["model"] = text
        else:
            car_data["model"] = ""
        context.user_data["car_data"] = car_data

        # Показываем данные для подтверждения
        confirm_text = f"✅ Подтвердите данные машины:\n\n"
        confirm_text += f"🚗 Номер: {car_data['number']}\n"
        confirm_text += f"🏭 Марка: {car_data.get('brand', 'Не указана')}\n"
        confirm_text += f"🚙 Модель: {car_data.get('model', 'Не указана')}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=confirm_text,
            reply_markup=get_confirm_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка подтверждения добавления"""
    current_state = context.user_data.get("state")

    if current_state == ADDING_DRIVER:
        await confirm_add_driver(update, context)
    elif current_state == ADDING_LOGIST:
        await confirm_add_logist(update, context)
    elif current_state == ADDING_CAR:
        await confirm_add_car(update, context)

    if update.callback_query:
        await update.callback_query.answer()

async def confirm_add_driver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение добавления водителя"""
    driver_data = context.user_data.get("driver_data", {})

    if not driver_data:
        return

    db = SessionLocal()
    try:
        # Создаем нового водителя
        new_driver = User(
            name=driver_data["name"],
            phone=driver_data["phone"],
            role="driver"
        )

        db.add(new_driver)
        db.commit()

        text = f"✅ Водитель успешно добавлен!\n\n"
        text += f"👤 Имя: {driver_data['name']}\n"
        text += f"📱 Телефон: {driver_data['phone']}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        text = f"❌ Ошибка добавления водителя: {str(e)}"
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close().effective_chat.id,
            text=text,
            reply_markup=get_admin_menu()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def confirm_add_logist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение добавления логиста"""
    logist_data = context.user_data.get("logist_data", {})

    if not logist_data:
        return

    db = SessionLocal()
    try:
        # Создаем нового логиста
        new_logist = User(
            name=logist_data["name"],
            phone=logist_data["phone"],
            role="logist"
        )

        db.add(new_logist)
        db.commit()

        text = f"✅ Логист успешно добавлен!\n\n"
        text += f"👤 Имя: {logist_data['name']}\n"
        text += f"📱 Телефон: {logist_data['phone']}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_menu()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        text = f"❌ Ошибка добавления логиста: {str(e)}"
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_menu()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка подтверждения"""
    await update.callback_query.answer()
    
    current_state = context.user_data.get("state")
    
    if current_state == ADDING_DRIVER:
        await confirm_add_driver(update, context)
    elif current_state == ADDING_LOGIST:
        await confirm_add_logist(update, context)
    elif current_state == ADDING_CAR:
        await confirm_add_car(update, context)

async def confirm_add_logist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение добавления логиста"""
    logist_data = context.user_data.get("logist_data", {})

    if not logist_data:
        return

    db = SessionLocal()
    try:
        # Создаем нового логиста
        new_logist = User(
            name=logist_data["name"],
            phone=logist_data["phone"],
            role="logist"
        )

        db.add(new_logist)
        db.commit()

        text = f"✅ Логист успешно добавлен!\n\n"
        text += f"👤 Имя: {logist_data['name']}\n"
        text += f"📱 Телефон: {logist_data['phone']}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        text = f"❌ Ошибка добавления логиста: {str(e)}"
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def confirm_add_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение добавления машины"""
    car_data = context.user_data.get("car_data", {})

    if not car_data:
        return

    db = SessionLocal()
    try:
        # Создаем новую машину
        new_car = Car(
            number=car_data["number"],
            brand=car_data["brand"],
            model=car_data["model"]
        )

        db.add(new_car)
        db.commit()

        text = f"✅ Машина успешно добавлена!\n\n"
        text += f"🔢 Номер: {car_data['number']}\n"
        text += f"🚗 Марка: {car_data['brand']}\n"
        text += f"🚙 Модель: {car_data['model']}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        text = f"❌ Ошибка добавления машины: {str(e)}"
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()=car_data.get("brand", ""),
            model=car_data.get("model", "")
        )

        db.add(new_car)
        db.commit()

        text = f"✅ Машина успешно добавлена!\n\n"
        text += f"🚗 Номер: {car_data['number']}\n"
        text += f"🏭 Марка: {car_data.get('brand', 'Не указана')}\n"
        text += f"🚙 Модель: {car_data.get('model', 'Не указана')}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_menu()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        text = f"❌ Ошибка добавления машины: {str(e)}"
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_menu()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()