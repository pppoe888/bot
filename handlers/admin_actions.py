from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car, Shift
from keyboards import get_back_keyboard, get_confirm_keyboard, get_admin_inline_keyboard, get_user_list_keyboard, get_edit_user_keyboard, get_manage_drivers_keyboard, get_manage_logists_keyboard, get_manage_cars_keyboard, get_admin_reports_keyboard, get_admin_shifts_keyboard, get_admin_reports_keyboard, get_admin_reports_keyboard, get_car_list_keyboard, get_edit_car_keyboard, get_admin_cars_keyboard, get_admin_reports_keyboard, get_admin_reports_keyboard, get_admin_reports_keyboard, get_cancel_keyboard
import states
from states import ADDING_DRIVER, ADDING_LOGIST, ADDING_CAR, EDITING_DRIVER, EDITING_LOGIST
from config import ADMIN_ID
from datetime import datetime

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

async def track_admin_message(update, context, message):
    """Отслеживает сообщения админки и удаляет старые"""
    # Удаляем все предыдущие сообщения перед добавлением нового
    if context.user_data.get("message_history"):
        for msg_id in context.user_data["message_history"]:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=msg_id
                )
            except:
                pass

    # Сохраняем только текущее сообщение
    context.user_data["message_history"] = [message.message_id]
    context.user_data["last_message_id"] = message.message_id

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
    elif current_state == "EDITING_CAR":
        await handle_edit_car_input(update, context, text)

async def handle_add_driver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать процесс добавления водителя"""
    await delete_previous_messages(update, context)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введите имя водителя:",
        reply_markup=get_cancel_keyboard()
    )
    context.user_data["state"] = ADDING_DRIVER
    context.user_data["driver_data"] = {}
    context.user_data["last_message_id"] = message.message_id

    if update.callback_query:
        await update.callback_query.answer()

async def handle_driver_input(update, context, text):
    """Обработка ввода данных водителя"""
    # Проверяем на отмену
    if text in ["Отменить", "Назад"]:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Добавление водителя отменено.",
            reply_markup=get_admin_inline_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
        return

    driver_data = context.user_data.get("driver_data", {})

    if "name" not in driver_data:
        driver_data["name"] = text
        context.user_data["driver_data"] = driver_data

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите номер телефона водителя:",
            reply_markup=get_cancel_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    elif "phone" not in driver_data:
        driver_data["phone"] = text
        context.user_data["driver_data"] = driver_data

        # Показываем данные для подтверждения
        confirm_text = f"Подтвердите данные водителя:\n\n"
        confirm_text += f"Имя: {driver_data['name']}\n"
        confirm_text += f"Телефон: {driver_data['phone']}"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=confirm_text,
            reply_markup=get_confirm_keyboard()
        )
        await track_admin_message(update, context, message)

async def handle_add_logist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать процесс добавления логиста"""
    await delete_previous_messages(update, context)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👤 Введите имя логиста:",
        reply_markup=get_cancel_keyboard()
    )
    context.user_data["state"] = ADDING_LOGIST
    context.user_data["logist_data"] = {}
    context.user_data["last_message_id"] = message.message_id

    if update.callback_query:
        await update.callback_query.answer()

async def handle_logist_input(update, context, text):
    """Обработка ввода данных логиста"""
    # Проверяем на отмену
    if text in ["❌ Отменить", "⬅️ Назад"]:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Добавление логиста отменено.",
            reply_markup=get_admin_inline_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
        return

    logist_data = context.user_data.get("logist_data", {})

    if "name" not in logist_data:
        logist_data["name"] = text
        context.user_data["logist_data"] = logist_data

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📱 Введите номер телефона логиста:",
            reply_markup=get_cancel_keyboard()
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
        await track_admin_message(update, context, message)

async def handle_add_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать процесс добавления машины"""
    await delete_previous_messages(update, context)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🚗 Введите номер машины:",
        reply_markup=get_cancel_keyboard()
    )
    context.user_data["state"] = ADDING_CAR
    context.user_data["car_data"] = {}
    context.user_data["last_message_id"] = message.message_id

    if update.callback_query:
        await update.callback_query.answer()

async def handle_car_input(update, context, text):
    """Обработка ввода данных машины"""
    # Проверяем на отмену
    if text in ["❌ Отменить", "⬅️ Назад"]:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Добавление машины отменено.",
            reply_markup=get_admin_inline_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
        return

    car_data = context.user_data.get("car_data", {})

    if "number" not in car_data:
        car_data["number"] = text
        context.user_data["car_data"] = car_data

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🏭 Введите марку машины (или напишите 'пропустить'):",
            reply_markup=get_cancel_keyboard()
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
            reply_markup=get_cancel_keyboard()
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
        await track_admin_message(update, context, message)

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
        await track_admin_message(update, context, message)

        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        text = f"❌ Ошибка добавления водителя: {str(e)}"
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
        await track_admin_message(update, context, message)

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
        await track_admin_message(update, context, message)

        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        text = f"❌ Ошибка добавления логиста: {str(e)}"
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
        await track_admin_message(update, context, message)

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
        await track_admin_message(update, context, message)

        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        text = f"❌ Ошибка добавления машины: {str(e)}"
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
        await track_admin_message(update, context, message)

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
        await track_admin_message(update, context, message)

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
    from keyboards import get_cancel_keyboard
    data_parts = update.callback_query.data.split("_")
    field = data_parts[1]  # name или phone
    driver_id = int(data_parts[3])

    context.user_data["state"] = EDITING_DRIVER
    context.user_data["edit_driver_id"] = driver_id
    context.user_data["edit_field"] = field

    field_text = "имя" if field == "name" else "номер телефона"

    await update.callback_query.edit_message_text(
        text=f"📝 Введите новое {field_text}:",
        reply_markup=get_cancel_keyboard()
    )

    await update.callback_query.answer()

async def handle_edit_driver_input(update, context, text):
    """Обработка ввода при редактировании водителя"""
    # Проверяем на отмену
    if text in ["❌ Отменить", "⬅️ Назад"]:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Редактирование отменено.",
            reply_markup=get_manage_drivers_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
        return

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
        await track_admin_message(update, context, message)

        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка редактирования: {str(e)}",
            reply_markup=get_manage_drivers_keyboard()
        )
        await track_admin_message(update, context, message)

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
        await track_admin_message(update, context, message)

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
    from keyboards import get_cancel_keyboard
    data_parts = update.callback_query.data.split("_")
    field = data_parts[1]  # name или phone
    logist_id = int(data_parts[3])

    context.user_data["state"] = EDITING_LOGIST
    context.user_data["edit_logist_id"] = logist_id
    context.user_data["edit_field"] = field

    field_text = "имя" if field == "name" else "номер телефона"

    await update.callback_query.edit_message_text(
        text=f"📝 Введите новое {field_text}:",
        reply_markup=get_cancel_keyboard()
    )

    await update.callback_query.answer()

async def handle_edit_logist_input(update, context, text):
    """Обработка ввода при редактировании логиста"""
    # Проверяем на отмену
    if text in ["❌ Отменить", "⬅️ Назад"]:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Редактирование отменено.",
            reply_markup=get_manage_logists_keyboard()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
        return

    logist_id = context.user_data.get("edit_logist_id")
    field = context.user_data.get("edit_field")

    if not context.user_data.get("edit_logist_id") or not field:
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
        await track_admin_message(update, context, message)

        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка редактирования: {str(e)}",
            reply_markup=get_manage_logists_keyboard()
        )
        await track_admin_message(update, context, message)

        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

# === УПРАВЛЕНИЕ АВТОМОБИЛЯМИ ===

async def manage_cars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Управление автомобилями"""
    from keyboards import get_manage_cars_keyboard

    text = "🚗 Управление автомобилями\n\nВыберите действие:"

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
        await track_admin_message(update, context, message)

        context.user_data["last_message_id"] = message.message_id

    await update.callback_query.answer()

async def show_cars_list(update: Update, context: ContextTypes.DEFAULT_TYPE, action_type: str = "view"):
    """Показать список автомобилей"""
    await delete_previous_messages(update, context)

    db = SessionLocal()
    try:
        cars = db.query(Car).all()

        if not cars:
            from keyboards import get_admin_cars_keyboard
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Автомобили не найдены.",
                reply_markup=get_admin_cars_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id
            return

        if action_type == "view":
            text = "🚗 Список автомобилей:\n\n"
            for car in cars:
                car_info = f"🚗 {car.number}"
                if car.brand:
                    car_info += f" ({car.brand}"
                    if car.model:
                        car_info += f" {car.model}"
                    car_info += ")"
                text += f"{car_info}\n"
                if car.fuel:
                    text += f"⛽ Топливо: {car.fuel}\n"
                if car.current_mileage:
                    text += f"📏 Пробег: {car.current_mileage} км\n"
                text += "───────────────\n"

            from keyboards import get_admin_cars_keyboard
            message = await context.bot.send_message(
                chatid=update.effective_chat.id,
                text=text,
                reply_markup=get_admin_cars_keyboard()
            )
            await track_admin_message(update, context, message)

        else:
            action_text = "редактирования" if action_type.startswith("edit") else "удаления"
            text = f"🚗 Выберите автомобиль для {action_text}:"

            from keyboards import get_car_list_keyboard
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=get_car_list_keyboard(cars, action_type)
            )
            await track_admin_message(update, context, message)

        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    if update.callback_query:
        await update.callback_query.answer()

async def edit_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Редактировать автомобиль"""
    await delete_previous_messages(update, context)

    car_id = int(update.callback_query.data.split("_")[2])

    db = SessionLocal()
    try:
        car = db.query(Car).filter(Car.id == car_id).first()

        if not car:
            await update.callback_query.answer("❌ Автомобиль не найден!")
            return

        text = f"📝 Редактирование автомобиля:\n\n"
        text += f"🚗 Номер: {car.number}\n"
        text += f"🏭 Марка: {car.brand or 'Не указана'}\n"
        text += f"🚙 Модель: {car.model or 'Не указана'}\n"
        text += f"⛽ Топливо: {car.fuel or 'Не указано'}\n"
        text += f"📏 Пробег: {car.current_mileage} км\n\n"
        text += "Выберите, что хотите изменить:"

        from keyboards import get_edit_car_keyboard
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_edit_car_keyboard(car_id)
        )
    finally:
        db.close()

    await update.callback_query.answer()

async def delete_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить автомобиль"""
    car_id = int(update.callback_query.data.split("_")[2])

    db = SessionLocal()
    try:
        car = db.query(Car).filter(Car.id == car_id).first()

        if not car:
            await update.callback_query.answer("❌ Автомобиль не найден!")
            return

        # Проверяем, есть ли активные смены с этим автомобилем
        active_shifts = db.query(Shift).filter(
            Shift.car_id == car_id,
            Shift.is_active == True
        ).count()

        if active_shifts > 0:
            text = f"❌ Нельзя удалить автомобиль {car.number}, он используется в активных сменах!"
        else:
            db.delete(car)
            db.commit()
            text = f"✅ Автомобиль {car.number} успешно удален!"

        from keyboards import get_admin_cars_keyboard
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_admin_cars_keyboard()
        )
    except Exception as e:
        from keyboards import get_admin_cars_keyboard
        text = f"❌ Ошибка удаления автомобиля: {str(e)}"
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_admin_cars_keyboard()
        )
    finally:
        db.close()

    await update.callback_query.answer()

async def edit_car_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать редактирование поля автомобиля"""
    data_parts = update.callback_query.data.split("_")
    field = data_parts[1]  # number, brand, model, fuel, mileage
    car_id = int(data_parts[3])

    context.user_data["state"] = "EDITING_CAR"
    context.user_data["edit_car_id"] = car_id
    context.user_data["edit_field"] = field

    field_names = {
        "number": "номер",
        "brand": "марку",
        "model": "модель", 
        "fuel": "тип топлива",
        "mileage": "пробег (км)"
    }

    field_text = field_names.get(field, "поле")

    await update.callback_query.edit_message_text(
        text=f"📝 Введите новое значение для поля '{field_text}':",
        reply_markup=get_cancel_keyboard()
    )

    await update.callback_query.answer()

async def handle_edit_car_input(update, context, text):
    """Обработка ввода при редактировании автомобиля"""
    # Проверяем на отмену
    if text in ["❌ Отменить", "⬅️ Назад"]:
        from keyboards import get_admin_cars_keyboard
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Редактирование отменено.",
            reply_markup=get_admin_cars_keyboard()
        )
        await track_admin_message(update, context, message)

        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
        return

    car_id = context.user_data.get("edit_car_id")
    field = context.user_data.get("edit_field")

    if not car_id or not field:
        return

    db = SessionLocal()
    try:
        car = db.query(Car).filter(Car.id == car_id).first()

        if not car:
            from keyboards import get_admin_cars_keyboard
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Автомобиль не найден!",
                reply_markup=get_admin_cars_keyboard()
            )
            await track_admin_message(update, context, message)

            context.user_data.clear()
            context.user_data["last_message_id"] = message.message_id
            return

        old_value = getattr(car, field)

        # Специальная обработка для пробега
        if field == "mileage":
            try:
                new_value = int(text)
                setattr(car, "current_mileage", new_value)
            except ValueError:
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Пробег должен быть числом!",
                    reply_markup=get_back_keyboard()
                )
                await track_admin_message(update, context, message)

                context.user_data["last_message_id"] = message.message_id
                return
        else:
            setattr(car, field, text)

        db.commit()

        field_names = {
            "number": "номер",
            "brand": "марка",
            "model": "модель", 
            "fuel": "тип топлива",
            "mileage": "пробег"
        }

        field_text = field_names.get(field, "поле")
        text_msg = f"✅ {field_text.capitalize()} автомобиля изменено!\n\n"
        text_msg += f"Было: {old_value if field != 'mileage' else getattr(car, 'current_mileage')}\n"
        text_msg += f"Стало: {text if field != 'mileage' else getattr(car, 'current_mileage')}"

        from keyboards import get_admin_cars_keyboard
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text_msg,
            reply_markup=get_admin_cars_keyboard()
        )
        await track_admin_message(update, context, message)

        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        from keyboards import get_admin_cars_keyboard
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка редактирования: {str(e)}",
            reply_markup=get_admin_cars_keyboard()
        )
        await track_admin_message(update, context, message)

        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

# === УПРАВЛЕНИЕ СМЕНАМИ ===

async def show_active_shifts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать активные смены"""
    await delete_previous_messages(update, context)

    db = SessionLocal()
    try:
        active_shifts = db.query(Shift).filter(Shift.is_active == True).all()

        if not active_shifts:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Активных смен не найдено.",
                reply_markup=get_admin_inline_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id
            return

        text = "🚛 Активные смены:\n\n"

        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = []

        for shift in active_shifts:
            driver = shift.driver
            car = shift.car

            car_info = car.number
            if car.brand:
                car_info += f" ({car.brand}"
                if car.model:
                    car_info += f" {car.model}"
                car_info += ")"

            start_time = shift.start_time.strftime('%H:%M')
            text += f"👤 {driver.name}\n"
            text += f"🚗 {car_info}\n"
            text += f"⏰ Начало: {start_time}\n"
            text += f"───────────────\n"

            # Кнопки для управления сменой
            keyboard.append([
                InlineKeyboardButton(f"✅ Завершить смену {driver.name}", callback_data=f"end_shift_{shift.id}")
            ])
            keyboard.append([
                InlineKeyboardButton(f"❌ Отменить смену {driver.name}", callback_data=f"cancel_shift_{shift.id}")
            ])

        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=reply_markup
        )
        await track_admin_message(update, context, message)

        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    if update.callback_query:
        await update.callback_query.answer()

async def end_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершить смену"""
    shift_id = int(update.callback_query.data.split("_")[2])

    db = SessionLocal()
    try:
        shift = db.query(Shift).filter(Shift.id == shift_id).first()

        if not shift:
            await update.callback_query.answer("❌ Смена не найдена!")
            return

        if not shift.is_active:
            await update.callback_query.answer("❌ Смена уже завершена!")
            return

        # Завершаем смену
        shift.end_time = datetime.now()
        shift.is_active = False
        db.commit()

        driver = shift.driver
        car = shift.car

        car_info = car.number
        if car.brand:
            car_info += f" ({car.brand}"
            if car.model:
                car_info += f" {car.model}"
            car_info += ")"

        # Уведомляем водителя о завершении смены
        try:
            if driver.telegram_id:
                driver_text = f"✅ Ваша смена завершена администратором\n\n"
                driver_text += f"🚗 Автомобиль: {car_info}\n"
                driver_text += f"⏰ Время начала: {shift.start_time.strftime('%H:%M')}\n"
                driver_text += f"⏰ Время окончания: {shift.end_time.strftime('%H:%M')}\n"
                driver_text += f"⏱️ Продолжительность: {(shift.end_time - shift.start_time).total_seconds() / 3600:.1f} ч"

                await context.bot.send_message(
                    chat_id=driver.telegram_id,
                    text=driver_text
                )
        except:
            pass

        text = f"✅ Смена водителя {driver.name} завершена!\n\n"
        text += f"🚗 Автомобиль: {car_info}\n"
        text += f"⏰ Время начала: {shift.start_time.strftime('%H:%M')}\n"
        text += f"⏰ Время окончания: {shift.end_time.strftime('%H:%M')}\n"
        text += f"⏱️ Продолжительность: {(shift.end_time - shift.start_time).total_seconds() / 3600:.1f} ч"

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К активным сменам", callback_data="show_active_shifts"),
                InlineKeyboardButton("🏠 Главная", callback_data="admin_panel")
            ]])
        )

    except Exception as e:
        await update.callback_query.edit_message_text(
            text=f"❌ Ошибка завершения смены: {str(e)}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К активным сменам", callback_data="show_active_shifts")
            ]])
        )
    finally:
        db.close()

    await update.callback_query.answer()

async def cancel_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменить смену"""
    shift_id = int(update.callback_query.data.split("_")[2])

    db = SessionLocal()
    try:
        shift = db.query(Shift).filter(Shift.id == shift_id).first()

        if not shift:
            await update.callback_query.answer("❌ Смена не найдена!")
            return

        if not shift.is_active:
            await update.callback_query.answer("❌ Смена уже завершена!")
            return

        driver = shift.driver
        car = shift.car

        car_info = car.number
        if car.brand:
            car_info += f" ({car.brand}"
            if car.model:
                car_info += f" {car.model}"
            car_info += ")"

        # Уведомляем водителя об отмене смены
        try:
            if driver.telegram_id:
                driver_text = f"❌ Ваша смена отменена администратором\n\n"
                driver_text += f"🚗 Автомобиль: {car_info}\n"
                driver_text += f"⏰ Время начала: {shift.start_time.strftime('%H:%M')}\n"
                driver_text += f"⏰ Время отмены: {datetime.now().strftime('%H:%M')}"

                await context.bot.send_message(
                    chat_id=driver.telegram_id,
                    text=driver_text
                )
        except:
            pass

        # Удаляем смену из базы данных
        db.delete(shift)
        db.commit()

        text = f"❌ Смена водителя {driver.name} отменена!\n\n"
        text += f"🚗 Автомобиль: {car_info}\n"
        text += f"⏰ Время начала: {shift.start_time.strftime('%H:%M')}\n"
        text += f"⏰ Время отмены: {datetime.now().strftime('%H:%M')}"

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К активным сменам", callback_data="show_active_shifts"),
                InlineKeyboardButton("🏠 Главная", callback_data="admin_panel")
            ]])
        )

    except Exception as e:
        await update.callback_query.edit_message_text(
            text=f"❌ Ошибка отмены смены: {str(e)}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К активным сменам", callback_data="show_active_shifts")
            ]])
        )
    finally:
        db.close()

    await update.callback_query.answer()

# === ИСТОРИЯ СМЕН И ОТЧЕТЫ ===

async def shifts_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """История смен"""
    from keyboards import get_admin_shifts_keyboard

    db = SessionLocal()
    try:
        # Получаем последние 10 завершенных смен
        completed_shifts = db.query(Shift).filter(
            Shift.is_active == False,
            Shift.end_time != None
        ).order_by(Shift.end_time.desc()).limit(10).all()

        if not completed_shifts:
            text = "📋 История смен пуста"
        else:
            text = "📋 История смен (последние 10):\n\n"

            for shift in completed_shifts:
                driver = shift.driver
                car = shift.car

                car_info = car.number
                if car.brand:
                    car_info += f" ({car.brand}"
                    if car.model:
                        car_info += f" {car.model}"
                    car_info += ")"

                start_time = shift.start_time.strftime('%d.%m %H:%M')
                end_time = shift.end_time.strftime('%d.%m %H:%M')
                duration = (shift.end_time - shift.start_time).total_seconds() / 3600

                text += f"👤 {driver.name}\n"
                text += f"🚗 {car_info}\n"
                text += f"📅 {start_time} - {end_time}\n"
                text += f"⏱️ {duration:.1f} ч\n"
                text += f"───────────────\n"

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
            await track_admin_message(update, context, message)

            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await update.callback_query.answer()

async def shifts_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отчет по сменам"""
    from keyboards import get_admin_reports_keyboard
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        # Статистика за последние 7 дней
        week_ago = datetime.now() - timedelta(days=7)

        week_shifts = db.query(Shift).filter(
            Shift.start_time >= week_ago
        ).count()

        completed_week = db.query(Shift).filter(
            Shift.start_time >= week_ago,
            Shift.is_active == False,
            Shift.end_time != None
        ).all()

        total_hours = 0
        if completed_week:
            for shift in completed_week:
                duration = (shift.end_time - shift.start_time).total_seconds() / 3600
                total_hours += duration

        avg_hours = total_hours / len(completed_week) if completed_week else 0

        text = "📊 Отчет по сменам (7 дней)\n\n"
        text += f"🚛 Всего смен: {week_shifts}\n"
        text += f"✅ Завершено: {len(completed_week)}\n"
        text += f"⏱️ Общее время: {total_hours:.1f} ч\n"
        text += f"📈 Среднее время: {avg_hours:.1f} ч"

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
            await track_admin_message(update, context, message)

            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await update.callback_query.answer()

async def cars_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отчет по машинам"""
    from keyboards import get_admin_reports_keyboard
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        cars = db.query(Car).all()
        week_ago = datetime.now() - timedelta(days=7)

        text = "📊 Отчет по машинам (7 дней)\n\n"

        for car in cars:
            car_info = car.number
            if car.brand:
                car_info += f" ({car.brand}"
                if car.model:
                    car_info += f" {car.model}"
                car_info += ")"

            car_shifts = db.query(Shift).filter(
                Shift.car_id == car.id,
                Shift.start_time >= week_ago
            ).count()

            text += f"🚗 {car_info}: {car_shifts} смен\n"

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
            await track_admin_message(update, context, message)

            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await update.callback_query.answer()

async def employees_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отчет по сотрудникам"""
    from keyboards import get_admin_reports_keyboard
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        drivers = db.query(User).filter(User.role == "driver").all()
        week_ago = datetime.now() - timedelta(days=7)

        text = "📊 Отчет по водителям (7 дней)\n\n"

        for driver in drivers:
            driver_shifts = db.query(Shift).filter(
                Shift.driver_id == driver.id,
                Shift.start_time >= week_ago
            ).count()

            completed_shifts = db.query(Shift).filter(
                Shift.driver_id == driver.id,
                Shift.start_time >= week_ago,
                Shift.is_active == False,
                Shift.end_time != None
            ).all()

            total_hours = 0
            if completed_shifts:
                for shift in completed_shifts:
                    duration = (shift.end_time - shift.start_time).total_seconds() / 3600
                    total_hours += duration

            text += f"👤 {driver.name}\n"
            text += f"   🚛 Смен: {driver_shifts}\n"
            text += f"   ⏱️ Часов: {total_hours:.1f}\n"

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
            await track_admin_message(update, context, message)

            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await update.callback_query.answer()