from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User
from keyboards import get_role_selection, get_phone_button, get_admin_menu, get_driver_menu, get_logist_menu
from states import WAITING_PHONE
from config import ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начальная команда - всегда показывает меню выбора роли"""
    
    # Очищаем состояние пользователя
    context.user_data.clear()

    # Удаляем предыдущие сообщения если есть
    try:
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )
        await update.message.delete()
    except:
        pass

    # Всегда показываем меню выбора роли
    keyboard = get_role_selection()
    text = "🔐 Добро пожаловать! Выберите вашу роль для входа в систему:"

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboard
    )
    context.user_data["last_message_id"] = message.message_id

async def create_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создание администратора"""
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав для создания администратора.")
        return

    db = SessionLocal()
    admin_user = db.query(User).filter(User.telegram_id == user_id).first()

    if admin_user:
        await update.message.reply_text("✅ Администратор уже существует.")
    else:
        admin_user = User(
            telegram_id=user_id,
            name="Администратор",
            phone="admin",
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        await update.message.reply_text("✅ Администратор создан успешно!")

    db.close()

async def handle_role_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора роли"""
    text = update.message.text

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
        # Проверяем права администратора
        if update.effective_user.id == ADMIN_ID:
            # Создаем или авторизуем админа
            db = SessionLocal()
            admin_user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
            
            if not admin_user:
                admin_user = User(
                    telegram_id=update.effective_user.id,
                    name="Администратор",
                    phone="admin",
                    role="admin"
                )
                db.add(admin_user)
                db.commit()
            
            db.close()
            
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Добро пожаловать, Администратор!",
                reply_markup=get_admin_menu()
            )
            context.user_data.clear()
            context.user_data["last_message_id"] = message.message_id
            return
        else:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ У вас нет прав администратора.\n\n🔐 Выберите вашу роль:",
                reply_markup=get_role_selection()
            )
            context.user_data["last_message_id"] = message.message_id
            return
            
    elif text == "🚛 Водитель":
        selected_role = "driver"
        role_text = "водителя"
    elif text == "📋 Логист":
        selected_role = "logist"
        role_text = "логиста"
    else:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Неверный выбор роли.\n\n🔐 Выберите вашу роль:",
            reply_markup=get_role_selection()
        )
        context.user_data["last_message_id"] = message.message_id
        return

    # Запрашиваем номер телефона для авторизации
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📱 Авторизация {role_text}\n\nПожалуйста, отправьте ваш номер телефона:",
        reply_markup=get_phone_button()
    )

    context.user_data["state"] = WAITING_PHONE
    context.user_data["selected_role"] = selected_role
    context.user_data["last_message_id"] = message.message_id

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка контакта"""
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

        # Отправляем приветственное сообщение с соответствующим меню
        if user_role == "driver":
            keyboard = get_driver_menu()
            text = f"✅ Добро пожаловать, водитель {user_name}!"
        elif user_role == "logist":
            keyboard = get_logist_menu()
            text = f"✅ Добро пожаловать, логист {user_name}!"
        else:
            keyboard = get_role_selection()
            text = "Выберите вашу роль:"

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=keyboard
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

    else:
        # Пользователь не найден
        db.close()

        try:
            if context.user_data.get("last_message_id"):
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data["last_message_id"]
                )
            await update.message.delete()
        except:
            pass

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ {selected_role.title()} с номером {phone} не найден в системе.\nОбратитесь к администратору.",
            reply_markup=get_role_selection()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id