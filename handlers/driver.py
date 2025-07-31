
from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car, Shift
from keyboards import get_car_keyboard
from datetime import datetime

async def start_shift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    
    # Проверяем, есть ли у водителя активная смена
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
    if not user:
        db.close()
        await update.message.reply_text("❌ Пользователь не найден.")
        return
    
    active_shift = db.query(Shift).filter(
        Shift.driver_id == user.id,
        Shift.status == "active"
    ).first()
    
    if active_shift:
        db.close()
        await update.message.reply_text("❌ У вас уже есть активная смена!")
        return
    
    # Получаем список доступных машин
    cars = db.query(Car).all()
    db.close()
    
    if not cars:
        await update.message.reply_text("❌ Нет доступных машин.")
        return
    
    await update.message.reply_text(
        "🚛 Выберите машину для начала смены:",
        reply_markup=get_car_keyboard(cars)
    )
