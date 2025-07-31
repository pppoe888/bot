from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from database import SessionLocal, User
from keyboards import get_driver_menu, get_admin_menu, get_phone_button
from states import WAITING_PHONE

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import ADMIN_ID

    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    # Если это админ и его нет в базе - создаем автоматически
    if update.effective_user.id == ADMIN_ID and not user:
        admin_user = User(
            telegram_id=ADMIN_ID,
            phone="admin",
            name=update.effective_user.first_name or "Администратор",
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        user = admin_user

    if user:
        # Получаем данные пользователя до закрытия сессии
        user_name = user.name
        # Проверяем является ли пользователь настоящим админом
        is_admin = (update.effective_user.id == ADMIN_ID)

        db.close()

        await update.message.reply_text(
            f"Добро пожаловать, {user_name}!",
            reply_markup=get_admin_menu() if is_admin else get_driver_menu()
        )
        context.user_data.clear()
    else:
        db.close()
        await update.message.reply_text(
            "Отправьте номер для входа:",
            reply_markup=get_phone_button()
        )
        context.user_data["state"] = WAITING_PHONE

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone = contact.phone_number
    user_id = update.effective_user.id

    db = SessionLocal()

    # Ищем пользователя по номеру телефона
    user = db.query(User).filter(User.phone == phone).first()

    if user:
        # Пользователь найден, обновляем telegram_id
        user.telegram_id = user_id
        db.commit()

        # Получаем имя пользователя до закрытия сессии
        user_name = user.name

        # Проверяем является ли пользователь настоящим админом
        from config import ADMIN_ID
        is_admin = (update.effective_user.id == ADMIN_ID)

        db.close()

        await update.message.reply_text(
            f"✅ Регистрация завершена! Добро пожаловать, {user_name}!",
            reply_markup=get_admin_menu() if is_admin else get_driver_menu()
        )
        context.user_data.clear()
    else:
        db.close()
        await update.message.reply_text(
            "❌ Ваш номер не найден в системе. Обратитесь к администратору."
        )

async def create_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import ADMIN_ID
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав для создания администратора.")
        return

    db = SessionLocal()

    # Проверяем, есть ли уже админ
    admin = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    if admin:
        await update.message.reply_text("✅ Вы уже зарегистрированы как администратор!")
    else:
        admin_user = User(
            telegram_id=update.effective_user.id,
            phone="admin",
            name=update.effective_user.first_name or "Администратор",
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        await update.message.reply_text("✅ Администратор создан!")

    db.close()

    await update.message.reply_text(
        "🛠️ Админ панель доступна",
        reply_markup=get_admin_menu()
    )