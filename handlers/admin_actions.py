from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений для админских действий"""
    admin_action = context.user_data.get("admin_action")

    if admin_action == "adding_driver":
        await handle_driver_adding(update, context)
    elif admin_action == "adding_car":
        await handle_car_adding(update, context)

async def handle_driver_adding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    driver_data = context.user_data.get("driver_data", {})
    text = update.message.text

    if "name" not in driver_data:
        driver_data["name"] = text
        context.user_data["driver_data"] = driver_data
        await update.message.reply_text("📞 Введите номер телефона водителя:")
    elif "phone" not in driver_data:
        driver_data["phone"] = text

        # Сохраняем водителя в базу
        db = SessionLocal()
        new_driver = User(
            phone=driver_data["phone"],
            name=driver_data["name"],
            role="driver"
        )
        db.add(new_driver)
        db.commit()
        db.close()

        keyboard = [[InlineKeyboardButton("⬅️ Назад к управлению", callback_data="manage_drivers")]]
        await update.message.reply_text(
            f"✅ Водитель {driver_data['name']} добавлен!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        # Очищаем данные
        context.user_data.clear()

async def handle_car_adding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    car_data = context.user_data.get("car_data", {})
    text = update.message.text

    if "number" not in car_data:
        car_data["number"] = text
        context.user_data["car_data"] = car_data
        await update.message.reply_text("🏭 Введите марку машины:")
    elif "brand" not in car_data:
        car_data["brand"] = text
        context.user_data["car_data"] = car_data
        await update.message.reply_text("🚗 Введите модель машины:")
    elif "model" not in car_data:
        car_data["model"] = text
        context.user_data["car_data"] = car_data
        await update.message.reply_text("⛽ Введите тип топлива:")
    elif "fuel" not in car_data:
        car_data["fuel"] = text
        context.user_data["car_data"] = car_data
        await update.message.reply_text("📏 Введите текущий пробег (км):")
    elif "mileage" not in car_data:
        try:
            mileage = int(text)
            car_data["mileage"] = mileage

            # Сохраняем машину в базу
            db = SessionLocal()
            new_car = Car(
                number=car_data["number"],
                brand=car_data["brand"],
                model=car_data["model"],
                fuel=car_data["fuel"],
                current_mileage=car_data["mileage"]
            )
            db.add(new_car)
            db.commit()
            db.close()

            keyboard = [[InlineKeyboardButton("⬅️ Назад к управлению", callback_data="manage_cars")]]
            await update.message.reply_text(
                f"✅ Машина {car_data['brand']} {car_data['model']} ({car_data['number']}) добавлена!",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            # Очищаем данные
            context.user_data.clear()
        except ValueError:
            await update.message.reply_text("❌ Пробег должен быть числом. Введите корректное значение:")