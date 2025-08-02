from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car, Shift, ShiftPhoto, CargoItem
from keyboards import get_car_inspection_keyboard, get_inspection_complete_keyboard, get_cargo_keyboard
from datetime import datetime
import states

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

async def car_inspection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало осмотра автомобиля"""
    user_id = update.effective_user.id
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            # Пользователь не найден - показываем детальную информацию для диагностики
            username = update.effective_user.first_name or "Пользователь"
            if update.effective_user.last_name:
                username += f" {update.effective_user.last_name}"

            text = f"❌ Пользователь не авторизован!\n\n"
            text += f"👤 Имя: {username}\n"
            text += f"🆔 Telegram ID: {user_id}\n\n"
            text += f"💡 Обратитесь к администратору для добавления в систему.\n\n"
            text += f"🔄 Для авторизации используйте команду /start"

            from telegram import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = [[
                InlineKeyboardButton("🔄 Попробовать авторизацию", callback_data="back_to_start")
            ]]

            try:
                if hasattr(update, 'callback_query') and update.callback_query:
                    await update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
                else:
                    message = await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=text,
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    context.user_data["last_message_id"] = message.message_id
            except:
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                context.user_data["last_message_id"] = message.message_id
            return

        # Проверяем, есть ли активная смена
        active_shift = db.query(Shift).filter(
            Shift.driver_id == user.id,
            Shift.is_active == True
        ).first()

        if active_shift:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="У вас уже есть активная смена! Завершите текущую смену перед новым осмотром.",
                reply_markup=get_car_inspection_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id
            return

        text = "🔍 ОСМОТР АВТОМОБИЛЯ\n\n"
        text += "Перед началом смены необходимо провести осмотр автомобиля.\n\n"
        text += "Вам потребуется сделать фотографии:\n"
        text += "• Передняя часть автомобиля\n"
        text += "• Задняя часть автомобиля\n"
        text += "• Левый борт\n"
        text += "• Правый борт\n"
        text += "• Уровень масла\n"
        text += "• Уровень антифриза\n"
        text += "• Салон автомобиля\n\n"
        text += "ВАЖНО: Используйте только камеру телефона! Фото из галереи запрещены."

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_car_inspection_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    finally:
        db.close()

async def start_inspection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать процесс осмотра с фотографиями"""
    user_id = update.effective_user.id
    db = SessionLocal()

    try:
        # Получаем список свободных машин
        busy_car_ids = db.query(Shift.car_id).filter(Shift.is_active == True).subquery()
        available_cars = db.query(Car).filter(Car.id.notin_(busy_car_ids)).all()

        if not available_cars:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Нет свободных автомобилей!"
            )
            context.user_data["last_message_id"] = message.message_id
            return

        # Создаем клавиатуру с доступными машинами
        keyboard = []
        for car in available_cars:
            car_name = car.number
            if car.brand:
                car_name += f" ({car.brand}"
                if car.model:
                    car_name += f" {car.model}"
                car_name += ")"
            keyboard.append([InlineKeyboardButton(car_name, callback_data=f"inspect_car_{car.id}")])

        keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            text="Выберите автомобиль для осмотра:",
            reply_markup=reply_markup
        )

    finally:
        db.close()

    await update.callback_query.answer()

async def select_car_for_inspection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор автомобиля для осмотра"""
    query = update.callback_query
    car_id = int(query.data.split("_")[2])

    # Сохраняем ID выбранной машины
    context.user_data["selected_car_id"] = car_id
    context.user_data["inspection_photos"] = {}
    context.user_data["state"] = states.PHOTO_CAR_FRONT

    text = "📸 НАЧИНАЕМ ОСМОТР\n\n"
    text += "Сделайте фото ПЕРЕДНЕЙ части автомобиля\n\n"
    text += "НАПОМИНАНИЕ:\n"
    text += "• ТОЛЬКО камера телефона\n"
    text += "• Съемка в реальном времени\n"
    text += "• Высокое качество\n\n"
    text += "Фото из галереи и скриншоты ЗАПРЕЩЕНЫ!"

    await query.edit_message_text(text=text)
    await query.answer()

async def handle_inspection_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фотографий при осмотре"""
    if not update.message or not update.message.photo:
        return False

    current_state = context.user_data.get("state")
    photo_states = [
        states.PHOTO_CAR_FRONT, states.PHOTO_CAR_BACK, 
        states.PHOTO_CAR_LEFT, states.PHOTO_CAR_RIGHT,
        states.PHOTO_COOLANT, states.PHOTO_OIL, states.PHOTO_INTERIOR
    ]

    if current_state not in photo_states:
        return False

    # Сохраняем фото в базу данных сразу
    photo = update.message.photo[-1]
    car_id = context.user_data.get("selected_car_id")

    if not car_id:
        await update.message.reply_text("Ошибка: автомобиль не выбран")
        return False

    # Определяем тип фото
    photo_type_map = {
        states.PHOTO_CAR_FRONT: "front",
        states.PHOTO_CAR_BACK: "back", 
        states.PHOTO_CAR_LEFT: "left",
        states.PHOTO_CAR_RIGHT: "right",
        states.PHOTO_OIL: "oil",
        states.PHOTO_COOLANT: "coolant",
        states.PHOTO_INTERIOR: "interior"
    }

    photo_type = photo_type_map.get(current_state)
    if not photo_type:
        return False

    # Сохраняем в базу
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
        if not user:
            await update.message.reply_text("Пользователь не найден")
            return False

        # Создаем временную смену для фото или используем существующую
        temp_shift_id = context.user_data.get("temp_shift_id")
        if not temp_shift_id:
            # Создаем временную запись смены
            temp_shift = Shift(
                driver_id=user.id,
                car_id=car_id,
                start_time=datetime.now(),
                is_active=False  # Пока что неактивная
            )
            db.add(temp_shift)
            db.flush()
            context.user_data["temp_shift_id"] = temp_shift.id
            temp_shift_id = temp_shift.id

        # Сохраняем фото
        shift_photo = ShiftPhoto(
            shift_id=temp_shift_id,
            photo_type=photo_type,
            file_id=photo.file_id
        )
        db.add(shift_photo)
        db.commit()

        print(f"Фото сохранено в БД: {photo_type} -> ID:{shift_photo.id}")

    except Exception as e:
        print(f"Ошибка сохранения фото в БД: {e}")
        await update.message.reply_text(f"Ошибка сохранения фото: {str(e)}")
        return False
    finally:
        db.close()

    # Удаляем сообщение с фото
    try:
        await update.message.delete()
    except:
        pass

    # Определяем следующий шаг
    next_step_map = {
        states.PHOTO_CAR_FRONT: (states.PHOTO_CAR_BACK, "Сделайте фото ЗАДНЕЙ части автомобиля"),
        states.PHOTO_CAR_BACK: (states.PHOTO_CAR_LEFT, "Сделайте фото ЛЕВОГО борта автомобиля"),
        states.PHOTO_CAR_LEFT: (states.PHOTO_CAR_RIGHT, "Сделайте фото ПРАВОГО борта автомобиля"),
        states.PHOTO_CAR_RIGHT: (states.PHOTO_OIL, "Сделайте фото уровня МАСЛА"),
        states.PHOTO_OIL: (states.PHOTO_COOLANT, "Сделайте фото уровня АНТИФРИЗА"),
        states.PHOTO_COOLANT: (states.PHOTO_INTERIOR, "Сделайте фото САЛОНА автомобиля"),
        states.PHOTO_INTERIOR: (None, "")
    }

    next_state, next_text = next_step_map[current_state]

    if next_state:
        context.user_data["state"] = next_state
        text = f"✅ Фото {photo_type} сохранено в БД!\n\n{next_text}\n\n"
        text += "НАПОМИНАНИЕ:\n"
        text += "• ТОЛЬКО камера телефона\n"
        text += "• Съемка в реальном времени\n"
        text += "• Высокое качество"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text
        )
        context.user_data["last_message_id"] = message.message_id
    else:
        # Все фото получены
        await complete_inspection(update, context)

    return True

async def complete_inspection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение осмотра автомобиля"""
    text = "✅ ОСМОТР ЗАВЕРШЕН!\n\n"
    text += "Все необходимые фотографии получены:\n"
    text += "• ✅ Передняя часть\n"
    text += "• ✅ Задняя часть\n"
    text += "• ✅ Левый борт\n"
    text += "• ✅ Правый борт\n"
    text += "• ✅ Уровень масла\n"
    text += "• ✅ Уровень антифриза\n"
    text += "• ✅ Салон\n\n"
    text += "Теперь можете начать смену!"

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=get_inspection_complete_keyboard()
    )
    context.user_data["last_message_id"] = message.message_id
    context.user_data["state"] = "inspection_complete"

async def confirm_start_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение начала смены после осмотра"""
    car_id = context.user_data.get("selected_car_id")
    temp_shift_id = context.user_data.get("temp_shift_id")

    if not car_id or not temp_shift_id:
        await update.callback_query.answer("Ошибка: данные осмотра не найдены!")
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
        car = db.query(Car).filter(Car.id == car_id).first()

        if not user or not car:
            await update.callback_query.answer("Ошибка: пользователь или автомобиль не найден!")
            return

        # Активируем временную смену
        temp_shift = db.query(Shift).filter(Shift.id == temp_shift_id).first()
        if temp_shift:
            temp_shift.is_active = True
            temp_shift.start_time = datetime.now()
        else:
            await update.callback_query.answer("Ошибка: временная смена не найдена!")
            return

        # Проверяем количество сохраненных фото
        photos_count = db.query(ShiftPhoto).filter(ShiftPhoto.shift_id == temp_shift_id).count()

        # Создаем тестовые товары для загрузки
        test_items = [
            {"number": "001", "name": "Товар А"},
            {"number": "002", "name": "Товар Б"},
            {"number": "003", "name": "Товар В"}
        ]

        for item in test_items:
            cargo_item = CargoItem(
                shift_id=temp_shift_id,
                item_number=item["number"],
                item_name=item["name"],
                is_loaded=False
            )
            db.add(cargo_item)

        db.commit()

        car_info = car.number
        if car.brand:
            car_info += f" ({car.brand}"
            if car.model:
                car_info += f" {car.model}"
            car_info += ")"

        text = f"✅ СМЕНА НАЧАТА!\n\n"
        text += f"🚗 Автомобиль: {car_info}\n"
        text += f"⏰ Время начала: {temp_shift.start_time.strftime('%H:%M')}\n"
        text += f"📸 Фотографии осмотра: {photos_count} шт. сохранено в БД\n\n"
        text += "Можете приступать к загрузке товаров!"

        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📦 К загрузке", callback_data="loading_cargo"),
                InlineKeyboardButton("🏠 Главная", callback_data="back_to_menu")
            ]])
        )

        # Очищаем только временные данные осмотра, сохраняя авторизацию
        temp_data_to_clear = ["selected_car_id", "temp_shift_id", "state", "inspection_photos"]
        for key in temp_data_to_clear:
            context.user_data.pop(key, None)

    except Exception as e:
        await update.callback_query.answer(f"Ошибка создания смены: {str(e)}")
    finally:
        db.close()

    await update.callback_query.answer()

async def loading_cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Загрузка товаров"""
    await delete_previous_messages(update, context)

    user_id = update.effective_user.id
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Пользователь не найден!"
            )
            context.user_data["last_message_id"] = message.message_id
            return

        # Получаем активную смену
        active_shift = db.query(Shift).filter(
            Shift.driver_id == user.id,
            Shift.is_active == True
        ).first()

        if not active_shift:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="У вас нет активной смены! Сначала начните смену."
            )
            context.user_data["last_message_id"] = message.message_id
            return

        # Получаем список товаров
        cargo_items = db.query(CargoItem).filter(CargoItem.shift_id == active_shift.id).all()

        if not cargo_items:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Нет товаров для загрузки."
            )
            context.user_data["last_message_id"] = message.message_id
            return

        text = "📦 ЗАГРУЗКА ТОВАРОВ\n\n"
        text += "Нажмите кнопку [ЗАГРУЗИТЬ] напротив каждого товара после его загрузки:\n\n"

        loaded_count = sum(1 for item in cargo_items if item.is_loaded)
        total_count = len(cargo_items)
        text += f"Загружено: {loaded_count}/{total_count}\n\n"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_cargo_keyboard(cargo_items)
        )
        context.user_data["last_message_id"] = message.message_id

    finally:
        db.close()

async def load_cargo_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отметить товар как загруженный"""
    query = update.callback_query
    item_id = int(query.data.split("_")[2])

    db = SessionLocal()
    try:
        cargo_item = db.query(CargoItem).filter(CargoItem.id == item_id).first()

        if not cargo_item:
            await query.answer("Товар не найден!")
            return

        cargo_item.is_loaded = True
        cargo_item.loaded_at = datetime.now()
        db.commit()

        # Обновляем список
        cargo_items = db.query(CargoItem).filter(CargoItem.shift_id == cargo_item.shift_id).all()

        loaded_count = sum(1 for item in cargo_items if item.is_loaded)
        total_count = len(cargo_items)

        text = "📦 ЗАГРУЗКА ТОВАРОВ\n\n"
        text += f"✅ Товар {cargo_item.item_number} загружен!\n\n"
        text += f"Загружено: {loaded_count}/{total_count}\n\n"

        await query.edit_message_text(
            text=text,
            reply_markup=get_cargo_keyboard(cargo_items)
        )

    except Exception as e:
        await query.answer(f"Ошибка: {str(e)}")
    finally:
        db.close()

    await query.answer()

async def ready_for_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Готов к доставке"""
    text = "🚚 ГОТОВ К ДОСТАВКЕ!\n\n"
    text += "✅ Все товары загружены\n"
    text += "✅ Можно отправляться на доставку\n\n"
    text += "Удачной поездки!"

    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")
        ]])
    )
    await update.callback_query.answer()