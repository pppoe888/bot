from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car, Shift
from keyboards import get_driver_menu
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

async def auto_delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup, delete_after: int = None):
    """Отправляет сообщение и автоматически удаляет его через заданное время (в секундах)"""
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )
    context.user_data["last_message_id"] = message.message_id

    if delete_after:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message.message_id)
        # async def delete_message(context: ContextTypes.DEFAULT_TYPE):
        #     try:
        #         await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message.message_id)
        #     except:
        #         pass
        # context.job_queue.run_once(delete_message, delete_after)


async def start_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать смену"""
    await delete_previous_messages(update, context)

    user_id = update.effective_user.id
    db = SessionLocal()

    try:
        # Проверяем, есть ли активная смена
        user = db.query(User).filter(User.telegram_id == user_id).first()
        active_shift = db.query(Shift).filter(
            Shift.driver_id == user.id,
            Shift.is_active == True
        ).first()

        if active_shift:
            await auto_delete_message(
            update, context,
            "⚠️ У вас уже есть активная смена. Завершите её перед началом новой.",
            get_driver_menu(),
            delete_after=None
        )
            return

        # Показываем список доступных машин
        cars = db.query(Car).all()

        if not cars:
            await auto_delete_message(
            update, context,
            "❌ Нет доступных машин для начала смены.",
            get_driver_menu(),
            delete_after=None
        )
            return

        keyboard = []
        for car in cars:
            car_text = f"{car.number}"
            if car.brand:
                car_text += f" ({car.brand}"
                if car.model:
                    car_text += f" {car.model}"
                car_text += ")"

            keyboard.append([InlineKeyboardButton(
                car_text, 
                callback_data=f"select_car_{car.id}"
            )])

        reply_markup = InlineKeyboardMarkup(keyboard)

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🚗 Выберите машину для начала смены:",
            reply_markup=reply_markup
        )
        context.user_data["last_message_id"] = message.message_id

    finally:
        db.close()

async def select_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор машины для смены"""
    query = update.callback_query
    car_id = int(query.data.split("_")[2])
    user_id = update.effective_user.id

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        car = db.query(Car).filter(Car.id == car_id).first()

        if not user or not car:
            await query.answer("❌ Ошибка выбора машины!")
            return

        # Создаем смену сразу без фотографий
        await create_shift_without_photos(update, context, car_id, user_id)

    except Exception as e:
        await query.answer(f"❌ Ошибка: {str(e)}")
    finally:
        db.close()

    await query.answer()

async def show_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать маршрут водителя"""
    await delete_previous_messages(update, context)

    user_id = update.effective_user.id
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()

        if not user:
            await auto_delete_message(
            update, context,
            "❌ Пользователь не найден.",
            get_driver_menu(),
            delete_after=5
        )
            return

        # Проверяем активную смену
        active_shift = db.query(Shift).filter(
            Shift.driver_id == user.id,
            Shift.is_active == True
        ).first()

        if not active_shift:
            await auto_delete_message(
            update, context,
            "❌ Нет активной смены. Начните смену для получения маршрута.",
            get_driver_menu(),
            delete_after=None
        )
            return

        # Здесь будет логика получения маршрута
        text = "🗺️ Ваш маршрут:\n\n"
        text += "📍 Точка 1: Склад (ул. Складская, 1)\n"
        text += "📍 Точка 2: Магазин А (ул. Торговая, 15)\n" 
        text += "📍 Точка 3: Магазин Б (ул. Центральная, 45)\n"
        text += "📍 Точка 4: Возврат на склад\n\n"
        text += "🕐 Примерное время: 4 часа\n"
        text += "📦 Груз: 15 коробок"

        await auto_delete_message(
            update, context,
            text,
            get_driver_menu(),
            delete_after=None
        )

    finally:
        db.close()

async def report_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сообщить о проблеме"""
    await delete_previous_messages(update, context)

    keyboard = [
        [InlineKeyboardButton("🚗 Проблема с машиной", callback_data="problem_car")],
        [InlineKeyboardButton("📦 Проблема с грузом", callback_data="problem_cargo")],
        [InlineKeyboardButton("🛣️ Проблема на дороге", callback_data="problem_road")],
        [InlineKeyboardButton("🏪 Проблема в точке доставки", callback_data="problem_delivery")],
        [InlineKeyboardButton("❓ Другая проблема", callback_data="problem_other")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="⚠️ Выберите тип проблемы:",
        reply_markup=reply_markup
    )
    context.user_data["last_message_id"] = message.message_id

async def handle_problem_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора типа проблемы"""
    query = update.callback_query
    problem_type = query.data.split("_")[1]

    problem_types = {
        "car": "🚗 Проблема с машиной",
        "cargo": "📦 Проблема с грузом", 
        "road": "🛣️ Проблема на дороге",
        "delivery": "🏪 Проблема в точке доставки",
        "other": "❓ Другая проблема"
    }

    selected_type = problem_types.get(problem_type, "❓ Другая проблема")

    text = f"⚠️ Тип проблемы: {selected_type}\n\n"
    text += "📝 Опишите проблему подробно. Ваше сообщение будет отправлено диспетчеру."

    await query.edit_message_text(text=text)

    # Сохраняем тип проблемы для дальнейшей обработки
    context.user_data["problem_type"] = selected_type
    context.user_data["awaiting_problem_description"] = True

    await query.answer()

async def handle_problem_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка описания проблемы"""
    if not context.user_data.get("awaiting_problem_description"):
        return False

    problem_type = context.user_data.get("problem_type", "❓ Другая проблема")
    description = update.message.text

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

        # Здесь можно сохранить проблему в базу данных
        # или отправить уведомление администратору/диспетчеру

        await update.message.delete()

        text = f"✅ Сообщение о проблеме отправлено!\n\n"
        text += f"⚠️ Тип: {problem_type}\n"
        text += f"📝 Описание: {description}\n\n"
        text += f"👤 Водитель: {user.name if user else 'Неизвестен'}\n"
        text += f"🕐 Время: {datetime.now().strftime('%H:%M')}\n\n"
        text += "📞 Диспетчер свяжется с вами в ближайшее время."

        # Отправляем уведомление администратору (можно добавить отдельную логику)
        from config import ADMIN_ID
        try:
            admin_text = f"🚨 НОВАЯ ПРОБЛЕМА ОТ ВОДИТЕЛЯ\n\n"
            admin_text += f"👤 Водитель: {user.name if user else 'Неизвестен'}\n"
            admin_text += f"📱 Телефон: {user.phone if user else 'Неизвестен'}\n"
            admin_text += f"⚠️ Тип: {problem_type}\n"
            admin_text += f"📝 Описание: {description}\n"
            admin_text += f"🕐 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_text
            )
        except:
            pass

        await auto_delete_message(
            update, context,
            text,
            get_driver_menu(),
            delete_after=None
        )

        # Очищаем временные данные
        context.user_data.pop("problem_type", None)
        context.user_data.pop("awaiting_problem_description", None)

        return True

    finally:
        db.close()

async def handle_shift_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фотографий при начале смены"""
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

    # Сохраняем фото
    photo = update.message.photo[-1]  # Берем фото наибольшего размера
    context.user_data["shift_photos"][current_state] = photo.file_id

    # Удаляем сообщение с фото
    try:
        await update.message.delete()
    except:
        pass

    # Определяем следующий шаг
    next_step_map = {
        states.PHOTO_CAR_FRONT: (states.PHOTO_CAR_BACK, "📷 Сделайте фото ЗАДНЕЙ части автомобиля"),
        states.PHOTO_CAR_BACK: (states.PHOTO_CAR_LEFT, "📷 Сделайте фото ЛЕВОЙ стороны автомобиля"),
        states.PHOTO_CAR_LEFT: (states.PHOTO_CAR_RIGHT, "📷 Сделайте фото ПРАВОЙ стороны автомобиля"),
        states.PHOTO_CAR_RIGHT: (states.PHOTO_COOLANT, "📷 Сделайте фото уровня ОХЛАЖДАЮЩЕЙ ЖИДКОСТИ"),
        states.PHOTO_COOLANT: (states.PHOTO_OIL, "📷 Сделайте фото уровня МАСЛА"),
        states.PHOTO_OIL: (states.PHOTO_INTERIOR, "📷 Сделайте фото САЛОНА автомобиля"),
        states.PHOTO_INTERIOR: (None, "")
    }

    next_state, next_text = next_step_map[current_state]

    if next_state:
        # Переходим к следующему фото
        context.user_data["state"] = next_state

        try:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Фото принято!\n\n{next_text}\n\n🚨 НАПОМИНАНИЕ:\n• ТОЛЬКО камера телефона\n• Съемка в реальном времени\n• Высокое качество\n\n🚫 Фото из галереи и скриншоты ЗАПРЕЩЕНЫ!"
            )
            context.user_data["last_message_id"] = message.message_id
        except:
            pass
    else:
        # Все фото получены, создаем смену
        await create_shift_with_photos(update, context)

    return True

async def create_shift_without_photos(update: Update, context: ContextTypes.DEFAULT_TYPE, car_id: int, user_id: int):
    """Создание смены без фотографий"""

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        car = db.query(Car).filter(Car.id == car_id).first()

        if not user or not car:
            await auto_delete_message(
            update, context,
            "❌ Ошибка создания смены!",
            get_driver_menu(),
            delete_after=5
        )
            return

        # Создаём новую смену
        new_shift = Shift(
            driver_id=user.id,
            car_id=car.id,
            start_time=datetime.now(),
            is_active=True
        )

        db.add(new_shift)
        db.commit()

        car_text = f"{car.number}"
        if car.brand:
            car_text += f" ({car.brand}"
            if car.model:
                car_text += f" {car.model}"
            car_text += ")"

        text = f"✅ Смена успешно начата!\n\n"
        text += f"🚗 Автомобиль: {car_text}\n"
        text += f"⏰ Время начала: {new_shift.start_time.strftime('%H:%M')}\n\n"
        text += "🚛 Можете приступать к работе!"

        # Отправляем уведомление администратору
        from config import ADMIN_ID
        try:
            admin_text = f"🚛 НОВАЯ СМЕНА НАЧАТА\n\n"
            admin_text += f"👤 Водитель: {user.name}\n"
            admin_text += f"🚗 Автомобиль: {car_text}\n"
            admin_text += f"🕐 Время: {new_shift.start_time.strftime('%d.%m.%Y %H:%M')}"

            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
        except:
            pass

        await auto_delete_message(
            update, context,
            text,
            get_driver_menu(),
            delete_after=None
        )

        # Очищаем временные данные
        context.user_data.clear()

    except Exception as e:
        await auto_delete_message(
            update, context,
            f"❌ Ошибка создания смены: {str(e)}",
            get_driver_menu(),
            delete_after=5
        )
    finally:
        db.close()