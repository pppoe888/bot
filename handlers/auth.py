from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from database import SessionLocal, User
from keyboards import (get_driver_menu, get_admin_menu, get_logist_menu, 
                      get_phone_button, get_role_selection)
from states import WAITING_PHONE, WAITING_ROLE_SELECTION

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import ADMIN_ID

    db = SessionLocal()

    try:
        # Удаляем предыдущие сообщения
        try:
            if context.user_data.get("last_message_id"):
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data["last_message_id"]
                )
            await update.message.delete()
        except:
            pass

        # Проверяем, есть ли пользователь в базе
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

        if user:
            # Пользователь найден - показываем соответствующее меню
            if user.role == "admin":
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Добро пожаловать, Администратор {user.name}!",
                    reply_markup=get_admin_menu()
                )
            elif user.role == "driver":
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Добро пожаловать, водитель {user.name}!",
                    reply_markup=get_driver_menu()
                )
            elif user.role == "logist":
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Добро пожаловать, логист {user.name}!",
                    reply_markup=get_logist_menu()
                )
            else:
                # Неизвестная роль
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Неизвестная роль пользователя. Обратитесь к администратору.",
                    reply_markup=get_role_selection()
                )
                context.user_data["state"] = WAITING_ROLE_SELECTION
        else:
            # Новый пользователь - предлагаем выбрать роль
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Добро пожаловать! Выберите вашу роль:",
                reply_markup=get_role_selection()
            )
            context.user_data["state"] = WAITING_ROLE_SELECTION

        context.user_data["last_message_id"] = message.message_id

    except Exception as e:
        print(f"Ошибка в start: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")
    finally:
        db.close()

async def handle_role_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора роли"""
    from config import ADMIN_ID

    if context.user_data.get("state") != WAITING_ROLE_SELECTION:
        return

    text = update.message.text
    selected_role = None

    # Удаляем предыдущие сообщения
    try:
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )
        await update.message.delete()
    except:
        pass

    if text == "👨‍💼 Администратор":
        # Проверяем, является ли пользователь настоящим админом
        if update.effective_user.id == ADMIN_ID:
            db = SessionLocal()
            admin_user = db.query(User).filter(User.telegram_id == ADMIN_ID).first()

            if not admin_user:
                # Создаем админа
                admin_user = User(
                    telegram_id=ADMIN_ID,
                    phone="admin",
                    name=update.effective_user.first_name or "Администратор",
                    role="admin"
                )
                db.add(admin_user)
                db.commit()
                db.refresh(admin_user)

            admin_name = admin_user.name
            db.close()

            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Добро пожаловать, Администратор {admin_name}!",
                reply_markup=get_admin_menu()
            )
            context.user_data.clear()
            context.user_data["last_message_id"] = message.message_id
        else:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ У вас нет прав администратора.\nВыберите другую роль:",
                reply_markup=get_role_selection()
            )
            context.user_data["last_message_id"] = message.message_id

    elif text == "📋 Логист":
        selected_role = "logist"
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Для авторизации логиста отправьте ваш номер телефона:",
            reply_markup=get_phone_button()
        )
        context.user_data["state"] = WAITING_PHONE
        context.user_data["selected_role"] = selected_role
        context.user_data["last_message_id"] = message.message_id

    elif text == "🚛 Водитель":
        selected_role = "driver"
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Для авторизации водителя отправьте ваш номер телефона:",
            reply_markup=get_phone_button()
        )
        context.user_data["state"] = WAITING_PHONE
        context.user_data["selected_role"] = selected_role
        context.user_data["last_message_id"] = message.message_id

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import ADMIN_ID

    # Админ не должен авторизовываться через номер телефона
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("❌ Администратор не может авторизоваться через номер телефона.")
        return

    contact = update.message.contact
    phone = contact.phone_number
    user_id = update.effective_user.id
    selected_role = context.user_data.get("selected_role", "driver")

    db = SessionLocal()

    # Ищем пользователя по номеру телефона и роли
    user = db.query(User).filter(
        User.phone == phone, 
        User.role == selected_role
    ).first()

    if user:
        # Пользователь найден, обновляем telegram_id
        user.telegram_id = user_id
        db.commit()

        user_name = user.name
        user_role = user.role
        db.close()

        # Удаляем предыдущие сообщения
        try:
            if context.user_data.get("last_message_id"):
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data["last_message_id"]
                )
            await update.message.delete()
        except:
            pass

        # Показываем соответствующее меню
        if user_role == "driver":
            keyboard = get_driver_menu()
            role_text = "водитель"
        elif user_role == "logist":
            keyboard = get_logist_menu()
            role_text = "логист"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Авторизация завершена! Добро пожаловать, {role_text} {user_name}!",
            reply_markup=keyboard
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
    else:
        db.close()
        # Удаляем предыдущее сообщение
        try:
            await update.message.delete()
        except:
            pass

        from keyboards import get_back_keyboard
        role_name = "логист" if selected_role == "logist" else "водитель"
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ваш номер не найден среди {role_name}ов. Обратитесь к администратору для добавления в систему.",
            reply_markup=get_back_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

async def create_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import ADMIN_ID
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав для создания администратора.")
        return

    db = SessionLocal()

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