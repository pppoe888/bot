
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
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ У вас уже есть активная смена. Завершите её перед началом новой.",
                reply_markup=get_driver_menu()
            )
            context.user_data["last_message_id"] = message.message_id
            return
        
        # Показываем список доступных машин
        cars = db.query(Car).all()
        
        if not cars:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Нет доступных машин для начала смены.",
                reply_markup=get_driver_menu()
            )
            context.user_data["last_message_id"] = message.message_id
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
        
        # Сохраняем данные для создания смены после фото
        context.user_data["selected_car_id"] = car_id
        context.user_data["shift_photos"] = {}
        context.user_data["state"] = states.PHOTO_CAR_FRONT
        
        car_text = f"{car.number}"
        if car.brand:
            car_text += f" ({car.brand}"
            if car.model:
                car_text += f" {car.model}"
            car_text += ")"
        
        text = f"📸 Автомобиль выбран: {car_text}\n\n"
        text += "Перед началом смены необходимо сделать фотографии автомобиля.\n\n"
        text += "📷 Сделайте фото ПЕРЕДНЕЙ части автомобиля\n\n"
        text += "⚠️ Используйте только камеру телефона!"
        
        await query.edit_message_text(text=text)
        
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
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Пользователь не найден.",
                reply_markup=get_driver_menu()
            )
            context.user_data["last_message_id"] = message.message_id
            return
        
        # Проверяем активную смену
        active_shift = db.query(Shift).filter(
            Shift.driver_id == user.id,
            Shift.is_active == True
        ).first()
        
        if not active_shift:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Нет активной смены. Начните смену для получения маршрута.",
                reply_markup=get_driver_menu()
            )
            context.user_data["last_message_id"] = message.message_id
            return
        
        # Здесь будет логика получения маршрута
        text = "🗺️ Ваш маршрут:\n\n"
        text += "📍 Точка 1: Склад (ул. Складская, 1)\n"
        text += "📍 Точка 2: Магазин А (ул. Торговая, 15)\n" 
        text += "📍 Точка 3: Магазин Б (ул. Центральная, 45)\n"
        text += "📍 Точка 4: Возврат на склад\n\n"
        text += "🕐 Примерное время: 4 часа\n"
        text += "📦 Груз: 15 коробок"
        
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_driver_menu()
        )
        context.user_data["last_message_id"] = message.message_id
        
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
        
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_driver_menu()
        )
        context.user_data["last_message_id"] = message.message_id
        
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
                text=f"✅ Фото принято!\n\n{next_text}\n\n⚠️ Используйте только камеру телефона!"
            )
            context.user_data["last_message_id"] = message.message_id
        except:
            pass
    else:
        # Все фото получены, создаем смену
        await create_shift_with_photos(update, context)
    
    return True

async def create_shift_with_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создание смены после получения всех фотографий"""
    car_id = context.user_data.get("selected_car_id")
    photos = context.user_data.get("shift_photos", {})
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        car = db.query(Car).filter(Car.id == car_id).first()
        
        if not user or not car:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Ошибка создания смены!",
                reply_markup=get_driver_menu()
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
        text += f"⏰ Время начала: {new_shift.start_time.strftime('%H:%M')}\n"
        text += f"📸 Получено фотографий: {len(photos)}/7\n\n"
        text += "Все необходимые фотографии загружены!"
        
        # Отправляем уведомление администратору с фотографиями
        from config import ADMIN_ID
        try:
            admin_text = f"📸 НОВАЯ СМЕНА НАЧАТА\n\n"
            admin_text += f"👤 Водитель: {user.name}\n"
            admin_text += f"🚗 Автомобиль: {car_text}\n"
            admin_text += f"🕐 Время: {new_shift.start_time.strftime('%d.%m.%Y %H:%M')}\n\n"
            admin_text += "Фотографии автомобиля:"
            
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
            
            # Отправляем фотографии администратору
            photo_names = {
                states.PHOTO_CAR_FRONT: "Передняя часть",
                states.PHOTO_CAR_BACK: "Задняя часть", 
                states.PHOTO_CAR_LEFT: "Левая сторона",
                states.PHOTO_CAR_RIGHT: "Правая сторона",
                states.PHOTO_COOLANT: "Охлаждающая жидкость",
                states.PHOTO_OIL: "Уровень масла",
                states.PHOTO_INTERIOR: "Салон"
            }
            
            for state, photo_id in photos.items():
                photo_name = photo_names.get(state, "Неизвестно")
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=photo_id,
                    caption=f"📷 {photo_name}"
                )
        except:
            pass
        
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_driver_menu()
        )
        context.user_data["last_message_id"] = message.message_id
        
        # Очищаем временные данные
        context.user_data.pop("selected_car_id", None)
        context.user_data.pop("shift_photos", None)
        context.user_data.pop("state", None)
        
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка создания смены: {str(e)}",
            reply_markup=get_driver_menu()
        )
    finally:
        db.close()
