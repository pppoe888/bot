from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car, Shift
from keyboards import get_admin_menu, get_back_keyboard, get_confirm_keyboard, get_admin_inline_keyboard, get_user_list_keyboard, get_edit_user_keyboard, get_manage_drivers_keyboard, get_manage_logists_keyboard
import states
from states import ADDING_DRIVER, ADDING_LOGIST, ADDING_CAR, EDITING_DRIVER, EDITING_LOGIST
from config import ADMIN_ID

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
    elif current_state == EDITING_DRIVER:
        await handle_edit_driver_input(update, context, text)
    elif current_state == EDITING_LOGIST:
        await handle_edit_logist_input(update, context, text)

async def handle_add_driver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать процесс добавления водителя"""
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

async def create_admin_entries(phone: str, name: str = "Администратор"):
    """Создает записи администратора как водителя и логиста"""
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже записи
        existing_driver = db.query(User).filter(
            User.phone == phone, 
            User.role == "driver"
        ).first()
        
        existing_logist = db.query(User).filter(
            User.phone == phone, 
            User.role == "logist"
        ).first()

        # Создаем запись водителя, если её нет
        if not existing_driver:
            driver = User(
                telegram_id=None,  # Не устанавливаем telegram_id сразу
                name=name,
                phone=phone,
                role="driver"
            )
            db.add(driver)

        # Создаем запись логиста, если её нет
        if not existing_logist:
            logist = User(
                telegram_id=None,  # Не устанавливаем telegram_id сразу
                name=name,
                phone=phone,
                role="logist"
            )
            db.add(logist)

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Ошибка создания записей администратора: {e}")
        return False
    finally:
        db.close()

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
        # Проверяем, существует ли уже пользователь с таким номером телефона
        existing_user = db.query(User).filter(User.phone == driver_data["phone"]).first()
        
        if existing_user:
            text = f"❌ Пользователь с номером {driver_data['phone']} уже существует!\n\n"
            text += f"👤 Имя: {existing_user.name}\n"
            text += f"📋 Роль: {existing_user.role}"
        else:
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
        db.close()

async def confirm_add_logist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение добавления логиста"""
    logist_data = context.user_data.get("logist_data", {})

    if not logist_data:
        return

    db = SessionLocal()
    try:
        # Проверяем, существует ли уже пользователь с таким номером телефона
        existing_user = db.query(User).filter(User.phone == logist_data["phone"]).first()
        
        if existing_user:
            text = f"❌ Пользователь с номером {logist_data['phone']} уже существует!\n\n"
            text += f"👤 Имя: {existing_user.name}\n"
            text += f"📋 Роль: {existing_user.role}"
        else:
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
        # Проверяем, существует ли уже машина с таким номером
        existing_car = db.query(Car).filter(Car.number == car_data["number"]).first()
        
        if existing_car:
            text = f"❌ Машина с номером {car_data['number']} уже существует!\n\n"
            text += f"🏭 Марка: {existing_car.brand or 'Не указана'}\n"
            text += f"🚙 Модель: {existing_car.model or 'Не указана'}"
        else:
            # Создаем новую машину
            new_car = Car(
                number=car_data["number"],
                brand=car_data.get("brand", ""),
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
        db.close()


# === УПРАВЛЕНИЕ ВОДИТЕЛЯМИ ===

async def show_drivers_list(update: Update, context: ContextTypes.DEFAULT_TYPE, action_type: str):
    """Показать список водителей"""
    await delete_previous_messages(update, context)

    db = SessionLocal()
    try:
        drivers = db.query(User).filter(User.role == "driver").all()
        
        if not drivers:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Водители не найдены.",
                reply_markup=get_manage_drivers_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id
            return

        action_text = "редактирования" if action_type.startswith("edit") else "удаления"
        text = f"👤 Выберите водителя для {action_text}:"
        
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_user_list_keyboard(drivers, action_type)
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    if update.callback_query:
        await update.callback_query.answer()

async def edit_driver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Редактировать водителя"""
    driver_id = int(update.callback_query.data.split("_")[2])
    
    db = SessionLocal()
    try:
        driver = db.query(User).filter(User.id == driver_id).first()
        
        if not driver:
            await update.callback_query.answer("❌ Водитель не найден!")
            return

        text = f"📝 Редактирование водителя:\n\n"
        text += f"👤 Имя: {driver.name}\n"
        text += f"📱 Телефон: {driver.phone}\n\n"
        text += "Выберите, что хотите изменить:"

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_edit_user_keyboard(driver_id, "driver")
        )
    finally:
        db.close()

    await update.callback_query.answer()

async def delete_driver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить водителя"""
    driver_id = int(update.callback_query.data.split("_")[2])
    
    db = SessionLocal()
    try:
        driver = db.query(User).filter(User.id == driver_id).first()
        
        if not driver:
            await update.callback_query.answer("❌ Водитель не найден!")
            return

        # Проверяем, есть ли активные смены
        active_shifts = db.query(Shift).filter(
            Shift.driver_id == driver_id,
            Shift.is_active == True
        ).count()

        if active_shifts > 0:
            text = f"❌ Нельзя удалить водителя {driver.name}, у него есть активные смены!"
        else:
            db.delete(driver)
            db.commit()
            text = f"✅ Водитель {driver.name} успешно удален!"

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_manage_drivers_keyboard()
        )
    except Exception as e:
        text = f"❌ Ошибка удаления водителя: {str(e)}"
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_manage_drivers_keyboard()
        )
    finally:
        db.close()

    await update.callback_query.answer()

async def edit_driver_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать редактирование поля водителя"""
    data_parts = update.callback_query.data.split("_")
    field = data_parts[1]  # name или phone
    driver_id = int(data_parts[3])
    
    context.user_data["state"] = EDITING_DRIVER
    context.user_data["edit_driver_id"] = driver_id
    context.user_data["edit_field"] = field
    
    field_text = "имя" if field == "name" else "номер телефона"
    
    await update.callback_query.edit_message_text(
        text=f"📝 Введите новое {field_text}:",
        reply_markup=get_back_keyboard()
    )
    
    await update.callback_query.answer()

async def handle_edit_driver_input(update, context, text):
    """Обработка ввода при редактировании водителя"""
    driver_id = context.user_data.get("edit_driver_id")
    field = context.user_data.get("edit_field")
    
    if not driver_id or not field:
        return
    
    db = SessionLocal()
    try:
        driver = db.query(User).filter(User.id == driver_id).first()
        
        if not driver:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Водитель не найден!",
                reply_markup=get_manage_drivers_keyboard()
            )
            context.user_data.clear()
            context.user_data["last_message_id"] = message.message_id
            return

        old_value = getattr(driver, field)
        setattr(driver, field, text)
        db.commit()
        
        field_text = "имя" if field == "name" else "номер телефона"
        text_msg = f"✅ {field_text.capitalize()} водителя изменено!\n\n"
        text_msg += f"Было: {old_value}\n"
        text_msg += f"Стало: {text}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text_msg,
            reply_markup=get_manage_drivers_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка редактирования: {str(e)}",
            reply_markup=get_manage_drivers_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

# === УПРАВЛЕНИЕ ЛОГИСТАМИ ===

async def show_logists_list(update: Update, context: ContextTypes.DEFAULT_TYPE, action_type: str):
    """Показать список логистов"""
    await delete_previous_messages(update, context)

    db = SessionLocal()
    try:
        logists = db.query(User).filter(User.role == "logist").all()
        
        if not logists:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Логисты не найдены.",
                reply_markup=get_manage_logists_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id
            return

        action_text = "редактирования" if action_type.startswith("edit") else "удаления"
        text = f"📋 Выберите логиста для {action_text}:"
        
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_user_list_keyboard(logists, action_type)
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    if update.callback_query:
        await update.callback_query.answer()

async def edit_logist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Редактировать логиста"""
    logist_id = int(update.callback_query.data.split("_")[2])
    
    db = SessionLocal()
    try:
        logist = db.query(User).filter(User.id == logist_id).first()
        
        if not logist:
            await update.callback_query.answer("❌ Логист не найден!")
            return

        text = f"📝 Редактирование логиста:\n\n"
        text += f"👤 Имя: {logist.name}\n"
        text += f"📱 Телефон: {logist.phone}\n\n"
        text += "Выберите, что хотите изменить:"

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_edit_user_keyboard(logist_id, "logist")
        )
    finally:
        db.close()

    await update.callback_query.answer()

async def delete_logist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить логиста"""
    logist_id = int(update.callback_query.data.split("_")[2])
    
    db = SessionLocal()
    try:
        logist = db.query(User).filter(User.id == logist_id).first()
        
        if not logist:
            await update.callback_query.answer("❌ Логист не найден!")
            return

        db.delete(logist)
        db.commit()
        text = f"✅ Логист {logist.name} успешно удален!"

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_manage_logists_keyboard()
        )
    except Exception as e:
        text = f"❌ Ошибка удаления логиста: {str(e)}"
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_manage_logists_keyboard()
        )
    finally:
        db.close()

    await update.callback_query.answer()

async def edit_logist_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать редактирование поля логиста"""
    data_parts = update.callback_query.data.split("_")
    field = data_parts[1]  # name или phone
    logist_id = int(data_parts[3])
    
    context.user_data["state"] = EDITING_LOGIST
    context.user_data["edit_logist_id"] = logist_id
    context.user_data["edit_field"] = field
    
    field_text = "имя" if field == "name" else "номер телефона"
    
    await update.callback_query.edit_message_text(
        text=f"📝 Введите новое {field_text}:",
        reply_markup=get_back_keyboard()
    )
    
    await update.callback_query.answer()

async def handle_edit_logist_input(update, context, text):
    """Обработка ввода при редактировании логиста"""
    logist_id = context.user_data.get("edit_logist_id")
    field = context.user_data.get("edit_field")
    
    if not logist_id or not field:
        return
    
    db = SessionLocal()
    try:
        logist = db.query(User).filter(User.id == logist_id).first()
        
        if not logist:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Логист не найден!",
                reply_markup=get_manage_logists_keyboard()
            )
            context.user_data.clear()
            context.user_data["last_message_id"] = message.message_id
            return

        old_value = getattr(logist, field)
        setattr(logist, field, text)
        db.commit()
        
        field_text = "имя" if field == "name" else "номер телефона"
        text_msg = f"✅ {field_text.capitalize()} логиста изменено!\n\n"
        text_msg += f"Было: {old_value}\n"
        text_msg += f"Стало: {text}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text_msg,
            reply_markup=get_manage_logists_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка редактирования: {str(e)}",
            reply_markup=get_manage_logists_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()
