from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car, Shift
from keyboards import get_car_keyboard
from datetime import datetime

async def start_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать смену водителя"""
    db = SessionLocal()

    try:
        # Проверяем, есть ли у водителя активная смена
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
        if not user:
            await update.message.reply_text("❌ Пользователь не найден.")
            return

        # Проверяем роль пользователя
        if user.role != "driver":
            await update.message.reply_text("❌ Эта функция доступна только водителям.")
            return

        active_shift = db.query(Shift).filter(
            Shift.driver_id == user.id,
            Shift.is_active == True
        ).first()

        if active_shift:
            await update.message.reply_text("❌ У вас уже есть активная смена!")
            return

        # Получаем список доступных машин
        cars = db.query(Car).all()

        if not cars:
            await update.message.reply_text("❌ Нет доступных машин.")
            return

        await update.message.reply_text(
            "🚗 Выберите машину для смены:",
            reply_markup=get_car_keyboard(cars)
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
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
        car = db.query(Car).filter(Car.id == car_id).first()

        if not user or not car:
            await update.callback_query.message.reply_text("❌ Ошибка при выборе машины.")
            return

        # Создаем новую смену
        new_shift = Shift(
            driver_id=user.id,
            car_id=car.id,
            start_time=datetime.utcnow(),
            is_active=True
        )

        db.add(new_shift)
        db.commit()

        car_info = f"{car.number}"
        if car.brand and car.model:
            car_info += f" ({car.brand} {car.model})"

        await update.callback_query.message.reply_text(
            f"✅ Смена начата!\n🚗 Машина: {car_info}\n⏰ Время начала: {new_shift.start_time.strftime('%H:%M %d.%m.%Y')}"
        )

    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ Ошибка при начале смены: {e}")
    finally:
        db.close()