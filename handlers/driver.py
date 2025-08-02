
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car, Shift, ShiftPhoto
from keyboards import get_driver_menu, get_problem_keyboard
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

async def driver_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовое меню водителя"""
    user_id = update.effective_user.id
    
    # Проверяем авторизацию
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id, User.role == "driver").first()
        if not user:
            # Пользователь не авторизован - просим поделиться контактом
            await request_contact(update, context)
            return
            
        # Пользователь авторизован - показываем меню
        await show_driver_menu(update, context, user.name)
        
    finally:
        db.close()

async def request_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрос контакта для авторизации"""
    from telegram import ReplyKeyboardMarkup, KeyboardButton
    
    await delete_previous_messages(update, context)
    
    text = "👋 Добро пожаловать!\n\n"
    text += "Для работы с системой необходимо авторизоваться.\n"
    text += "Поделитесь контактом для входа в систему."
    
    # Создаем клавиатуру с кнопкой контакта
    contact_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📞 Поделиться контактом", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=contact_keyboard
    )
    context.user_data["last_message_id"] = message.message_id

async def show_driver_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_name: str):
    """Показать основное меню водителя"""
    await delete_previous_messages(update, context)
    
    text = f"👋 Добро пожаловать, {user_name}!\n\n"
    text += "Выберите действие:"
    
    keyboard = [
        [InlineKeyboardButton("🔍 Осмотр автомобиля", callback_data="car_inspection")],
        [InlineKeyboardButton("⚠️ Сообщить о проблеме", callback_data="report_problem")],
        [InlineKeyboardButton("📊 Мои смены", callback_data="my_shifts")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup
    )
    context.user_data["last_message_id"] = message.message_id

async def car_inspection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало осмотра автомобиля"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.telegram_id == user_id, User.role == "driver").first()
        if not user:
            await query.edit_message_text("❌ Ошибка авторизации!")
            return
            
        # Проверяем активную смену
        active_shift = db.query(Shift).filter(
            Shift.driver_id == user.id,
            Shift.is_active == True
        ).first()
        
        if active_shift:
            text = "⚠️ У вас уже есть активная смена!\n\n"
            text += "Завершите текущую смену перед новым осмотром."
            
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
            return
            
        # Получаем свободные автомобили
        busy_car_ids = db.query(Shift.car_id).filter(Shift.is_active == True).all()
        busy_ids = [car_id[0] for car_id in busy_car_ids]
        available_cars = db.query(Car).filter(~Car.id.in_(busy_ids)).all()
        
        if not available_cars:
            text = "❌ Нет свободных автомобилей!"
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
            return
            
        # Показываем список автомобилей
        text = "🚗 Выберите автомобиль для осмотра:\n\n"
        
        keyboard = []
        for car in available_cars:
            car_name = car.number
            if car.brand:
                car_name += f" ({car.brand}"
                if car.model:
                    car_name += f" {car.model}"
                car_name += ")"
            keyboard.append([InlineKeyboardButton(car_name, callback_data=f"select_car_{car.id}")])
            
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")])
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        
    finally:
        db.close()

async def select_car_for_inspection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор автомобиля для осмотра"""
    query = update.callback_query
    await query.answer()
    
    car_id = int(query.data.split("_")[2])
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id, User.role == "driver").first()
        car = db.query(Car).filter(Car.id == car_id).first()
        
        if not user or not car:
            await query.edit_message_text("❌ Ошибка: пользователь или автомобиль не найден!")
            return
            
        # Проверяем, что машина еще свободна
        existing_shift = db.query(Shift).filter(
            Shift.car_id == car_id,
            Shift.is_active == True
        ).first()
        
        if existing_shift:
            await query.edit_message_text("❌ Автомобиль уже занят!")
            return
            
        # Создаем временную смену для осмотра
        temp_shift = Shift(
            driver_id=user.id,
            car_id=car_id,
            start_time=datetime.now(),
            is_active=False  # Неактивная до завершения осмотра
        )
        
        db.add(temp_shift)
        db.commit()
        
        # Сохраняем данные для фотосессии
        context.user_data["inspection_shift_id"] = temp_shift.id
        context.user_data["inspection_car_id"] = car_id
        context.user_data["current_photo_step"] = "front"
        
        car_info = car.number
        if car.brand:
            car_info += f" ({car.brand}"
            if car.model:
                car_info += f" {car.model}"
            car_info += ")"
            
        text = f"📸 ОСМОТР АВТОМОБИЛЯ\n\n"
        text += f"🚗 Автомобиль: {car_info}\n\n"
        text += "Необходимо сделать фотографии:\n"
        text += "1️⃣ Передняя часть\n"
        text += "2️⃣ Задняя часть\n"
        text += "3️⃣ Левый борт\n"
        text += "4️⃣ Правый борт\n"
        text += "5️⃣ Уровень масла\n"
        text += "6️⃣ Уровень антифриза\n"
        text += "7️⃣ Салон автомобиля\n\n"
        text += "📷 Сделайте фото ПЕРЕДНЕЙ части автомобиля"
        
        await query.edit_message_text(text=text)
        
    finally:
        db.close()

async def handle_inspection_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фотографий при осмотре"""
    if not update.message or not update.message.photo:
        return False
        
    shift_id = context.user_data.get("inspection_shift_id")
    current_step = context.user_data.get("current_photo_step")
    
    if not shift_id or not current_step:
        return False
        
    # Сохраняем фото в базу данных
    photo = update.message.photo[-1]  # Берем фото наибольшего размера
    
    db = SessionLocal()
    try:
        # Создаем запись фото в базе
        shift_photo = ShiftPhoto(
            shift_id=shift_id,
            photo_type=current_step,
            file_id=photo.file_id
        )
        
        db.add(shift_photo)
        db.commit()
        
        # Удаляем сообщение с фото
        try:
            await update.message.delete()
        except:
            pass
            
        # Определяем следующий шаг
        photo_steps = {
            "front": ("back", "📷 Сделайте фото ЗАДНЕЙ части автомобиля"),
            "back": ("left", "📷 Сделайте фото ЛЕВОГО борта автомобиля"),
            "left": ("right", "📷 Сделайте фото ПРАВОГО борта автомобиля"),
            "right": ("oil", "📷 Сделайте фото уровня МАСЛА"),
            "oil": ("coolant", "📷 Сделайте фото уровня АНТИФРИЗА"),
            "coolant": ("interior", "📷 Сделайте фото САЛОНА автомобиля"),
            "interior": (None, "")
        }
        
        next_step, next_text = photo_steps.get(current_step, (None, ""))
        
        if next_step:
            # Переходим к следующему фото
            context.user_data["current_photo_step"] = next_step
            
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Фото сохранено!\n\n{next_text}"
            )
            context.user_data["last_message_id"] = message.message_id
        else:
            # Все фото получены - завершаем осмотр
            await complete_inspection(update, context)
            
    except Exception as e:
        print(f"Ошибка сохранения фото: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Ошибка сохранения фото. Попробуйте еще раз."
        )
    finally:
        db.close()
        
    return True

async def complete_inspection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение осмотра автомобиля"""
    shift_id = context.user_data.get("inspection_shift_id")
    
    if not shift_id:
        return
        
    db = SessionLocal()
    try:
        # Активируем смену
        shift = db.query(Shift).filter(Shift.id == shift_id).first()
        if shift:
            shift.is_active = True
            shift.start_time = datetime.now()
            db.commit()
            
            car_info = shift.car.number
            if shift.car.brand:
                car_info += f" ({shift.car.brand"
                if shift.car.model:
                    car_info += f" {shift.car.model}"
                car_info += ")"
                
            text = "✅ ОСМОТР ЗАВЕРШЕН!\n\n"
            text += f"🚗 Автомобиль: {car_info}\n"
            text += f"⏰ Смена начата: {shift.start_time.strftime('%H:%M')}\n\n"
            text += "Все фотографии сохранены в системе.\n"
            text += "Можете приступать к работе!"
            
            # Отправляем уведомление администратору
            from config import ADMIN_ID
            try:
                admin_text = f"🚗 НОВАЯ СМЕНА НАЧАТА\n\n"
                admin_text += f"👤 Водитель: {shift.driver.name}\n"
                admin_text += f"🚗 Автомобиль: {car_info}\n"
                admin_text += f"⏰ Время: {shift.start_time.strftime('%d.%m.%Y %H:%M')}\n"
                admin_text += f"📸 Фото осмотра: Сохранены"
                
                await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
            except:
                pass
                
            keyboard = [[InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")]]
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            context.user_data["last_message_id"] = message.message_id
            
            # Очищаем временные данные
            context.user_data.pop("inspection_shift_id", None)
            context.user_data.pop("inspection_car_id", None)
            context.user_data.pop("current_photo_step", None)
            
    finally:
        db.close()

async def report_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сообщить о проблеме"""
    query = update.callback_query
    await query.answer()
    
    text = "⚠️ Выберите тип проблемы:"
    
    keyboard = [
        [InlineKeyboardButton("🚗 Проблема с машиной", callback_data="problem_car")],
        [InlineKeyboardButton("📦 Проблема с грузом", callback_data="problem_cargo")],
        [InlineKeyboardButton("🛣️ Проблема на дороге", callback_data="problem_road")],
        [InlineKeyboardButton("📍 Проблема в точке доставки", callback_data="problem_delivery")],
        [InlineKeyboardButton("❓ Другая проблема", callback_data="problem_other")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
    ]
    
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_problem_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора типа проблемы"""
    query = update.callback_query
    await query.answer()
    
    problem_type = query.data.split("_")[1]
    
    problem_types = {
        "car": "Проблема с машиной",
        "cargo": "Проблема с грузом",
        "road": "Проблема на дороге", 
        "delivery": "Проблема в точке доставки",
        "other": "Другая проблема"
    }
    
    selected_type = problem_types.get(problem_type, "Другая проблема")
    
    text = f"⚠️ Тип проблемы: {selected_type}\n\n"
    text += "Опишите проблему подробно. Ваше сообщение будет отправлено диспетчеру."
    
    await query.edit_message_text(text=text)
    
    # Сохраняем тип проблемы для дальнейшей обработки
    context.user_data["problem_type"] = selected_type
    context.user_data["awaiting_problem_description"] = True

async def handle_problem_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка описания проблемы"""
    if not context.user_data.get("awaiting_problem_description"):
        return False
        
    problem_type = context.user_data.get("problem_type", "Другая проблема")
    description = update.message.text
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
        
        await update.message.delete()
        
        text = f"✅ Сообщение о проблеме отправлено!\n\n"
        text += f"📋 Тип: {problem_type}\n"
        text += f"📝 Описание: {description}\n\n"
        text += f"👤 Водитель: {user.name if user else 'Неизвестен'}\n"
        text += f"⏰ Время: {datetime.now().strftime('%H:%M')}\n\n"
        text += "Диспетчер свяжется с вами в ближайшее время."
        
        # Отправляем уведомление администратору
        from config import ADMIN_ID
        try:
            admin_text = f"🚨 НОВАЯ ПРОБЛЕМА ОТ ВОДИТЕЛЯ\n\n"
            admin_text += f"👤 Водитель: {user.name if user else 'Неизвестен'}\n"
            admin_text += f"📱 Телефон: {user.phone if user else 'Неизвестен'}\n"
            admin_text += f"📋 Тип: {problem_type}\n"
            admin_text += f"📝 Описание: {description}\n"
            admin_text += f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
        except:
            pass
            
        keyboard = [[InlineKeyboardButton("🔙 В главное меню", callback_data="back_to_menu")]]
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data["last_message_id"] = message.message_id
        
        # Очищаем временные данные
        context.user_data.pop("problem_type", None)
        context.user_data.pop("awaiting_problem_description", None)
        
        return True
        
    finally:
        db.close()

async def my_shifts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать мои смены"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.telegram_id == user_id, User.role == "driver").first()
        if not user:
            await query.edit_message_text("❌ Ошибка авторизации!")
            return
            
        # Получаем смены пользователя
        shifts = db.query(Shift).filter(Shift.driver_id == user.id).order_by(Shift.start_time.desc()).limit(10).all()
        
        if not shifts:
            text = "📊 У вас пока нет смен"
        else:
            text = "📊 МОИ СМЕНЫ\n\n"
            
            for shift in shifts:
                car_info = shift.car.number
                if shift.car.brand:
                    car_info += f" ({shift.car.brand})"
                    
                status = "🟢 Активна" if shift.is_active else "🔴 Завершена"
                start_time = shift.start_time.strftime('%d.%m %H:%M')
                
                text += f"🚗 {car_info}\n"
                text += f"📅 {start_time}\n"
                text += f"📊 {status}\n"
                
                if not shift.is_active and shift.end_time:
                    end_time = shift.end_time.strftime('%d.%m %H:%M')
                    duration = (shift.end_time - shift.start_time).total_seconds() / 3600
                    text += f"🏁 {end_time}\n"
                    text += f"⏱️ {duration:.1f} ч\n"
                    
                text += "───────────────\n"
                
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        
    finally:
        db.close()

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.telegram_id == user_id, User.role == "driver").first()
        if not user:
            await request_contact(update, context)
            return
            
        await show_driver_menu(update, context, user.name)
        
    finally:
        db.close()
