from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car

async def start_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало смены водителя"""
    db = SessionLocal()
    try:
        # Проверяем авторизацию пользователя
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

        if not user or user.role != "driver":
            await update.message.reply_text("❌ Вы не авторизованы как водитель.")
            return

        # Получаем список доступных машин
        cars = db.query(Car).all()

        if not cars:
            await update.message.reply_text("❌ Нет доступных машин для начала смены.")
            return

        # Создаем клавиатуру с машинами
        keyboard = []
        for car in cars:
            car_text = f"🚗 {car.number}"
            if car.model:
                car_text += f" ({car.model})"
            keyboard.append([InlineKeyboardButton(car_text, callback_data=f"select_car_{car.id}")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🚗 Выберите машину для начала смены:",
            reply_markup=reply_markup
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    finally:
        db.close()

async def select_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор машины для смены"""
    await update.callback_query.answer()

    car_id = int(update.callback_query.data.split("_")[-1])

    db = SessionLocal()
    try:
        # Проверяем авторизацию
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

        if not user or user.role != "driver":
            await update.callback_query.message.reply_text("❌ Вы не авторизованы как водитель.")
            return

        # Получаем информацию о машине
        car = db.query(Car).filter(Car.id == car_id).first()

        if not car:
            await update.callback_query.message.reply_text("❌ Машина не найдена.")
            return

        # Отправляем подтверждение
        text = f"✅ Смена начата!\n\n🚗 Машина: {car.number}"
        if car.model:
            text += f" ({car.model})"

        await update.callback_query.edit_message_text(text)

    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ Ошибка: {str(e)}")
    finally:
        db.close()
from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car, Shift
from keyboards import get_car_selection_keyboard, get_driver_menu
from datetime import datetime

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
    
    db = SessionLocal()
    try:
        # Получаем список доступных машин
        cars = db.query(Car).all()
        
        if not cars:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Нет доступных машин для начала смены.",
                reply_markup=get_driver_menu()
            )
            context.user_data["last_message_id"] = message.message_id
            return
        
        text = "🚗 Выберите машину для начала смены:"
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_car_selection_keyboard(cars)
        )
        context.user_data["last_message_id"] = message.message_id
        
    except Exception as e:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка загрузки машин: {str(e)}",
            reply_markup=get_driver_menu()
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def select_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор машины для смены"""
    await update.callback_query.answer()
    
    car_id = int(update.callback_query.data.split("_")[2])
    
    db = SessionLocal()
    try:
        # Получаем информацию о машине
        car = db.query(Car).filter(Car.id == car_id).first()
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
        
        if not car or not user:
            await update.callback_query.edit_message_text("❌ Ошибка выбора машины.")
            return
        
        # Проверяем, нет ли активной смены у водителя
        active_shift = db.query(Shift).filter(
            Shift.driver_id == user.id,
            Shift.is_active == True
        ).first()
        
        if active_shift:
            await update.callback_query.edit_message_text(
                "❌ У вас уже есть активная смена. Завершите её перед началом новой."
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
        
        text = f"✅ Смена начата!\n\n"
        text += f"🚗 Машина: {car.number}\n"
        text += f"🏭 Марка: {car.brand}\n"
        text += f"🚙 Модель: {car.model}\n"
        text += f"⏰ Время начала: {new_shift.start_time.strftime('%H:%M')}"
        
        await update.callback_query.edit_message_text(text)
        
    except Exception as e:
        await update.callback_query.edit_message_text(f"❌ Ошибка начала смены: {str(e)}")
    finally:
        db.close()
