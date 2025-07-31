from telegram import Update
from telegram.ext import ContextTypes
from database import SessionLocal, User
from keyboards import get_phone_request_keyboard, get_role_selection, get_driver_menu, get_logist_menu, get_admin_menu
from config import ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = update.effective_user.id

    # Проверяем, является ли пользователь администратором
    if user_id == ADMIN_ID:
        keyboard = get_admin_menu()
        text = "👑 Добро пожаловать, администратор!\n\n🛠️ Админ панель"
        message = await update.message.reply_text(text, reply_markup=keyboard)
        context.user_data["last_message_id"] = message.message_id
        return

    # Проверяем, есть ли пользователь в базе
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == user_id).first()
    db.close()

    if user:
        # Пользователь уже зарегистрирован
        if user.role == "driver":
            keyboard = get_driver_menu()
            text = f"🚛 Добро пожаловать, {user.name}!\n\nВы вошли как водитель."
        elif user.role == "logist":
            keyboard = get_logist_menu()
            text = f"📋 Добро пожаловать, {user.name}!\n\nВы вошли как логист."
        else:
            keyboard = get_role_selection()
            text = "Выберите вашу роль:"
    else:
        # Новый пользователь
        keyboard = get_role_selection()
        text = "👋 Добро пожаловать!\n\nДля начала работы выберите вашу роль:"

    message = await update.message.reply_text(text, reply_markup=keyboard)
    context.user_data["last_message_id"] = message.message_id

async def create_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создание администратора"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
        return

    db = SessionLocal()
    try:
        # Проверяем, есть ли уже админ в базе
        admin = db.query(User).filter(User.telegram_id == ADMIN_ID).first()

        if admin:
            await update.message.reply_text("✅ Администратор уже существует!")
            return

        # Создаём админа
        new_admin = User(
            telegram_id=ADMIN_ID,
            name="Администратор",
            phone="admin",
            role="admin"
        )

        db.add(new_admin)
        db.commit()

        await update.message.reply_text("✅ Администратор успешно создан!")

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка создания администратора: {e}")
    finally:
        db.close()

async def handle_role_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора роли"""
    role_text = update.message.text

    if role_text == "👨‍💼 Администратор":
        selected_role = "admin"
        role_display = "администратор"
    elif role_text == "📋 Логист":
        selected_role = "logist"
        role_display = "логист"
    elif role_text == "🚛 Водитель":
        selected_role = "driver"
        role_display = "водитель"
    else:
        return

    context.user_data["selected_role"] = selected_role

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

    # Запрашиваем номер телефона
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📱 Для авторизации как {role_display} поделитесь номером телефона:",
        reply_markup=get_phone_request_keyboard()
    )
    context.user_data["last_message_id"] = message.message_id

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка получения контакта для авторизации"""
    # Проверяем, что это не администратор - администратор не должен авторизовываться через номер телефона
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
            text = f"🚛 Добро пожаловать, {user_name}!\n\nВы успешно авторизованы как водитель."
        elif user_role == "logist":
            keyboard = get_logist_menu()
            text = f"📋 Добро пожаловать, {user_name}!\n\nВы успешно авторизованы как логист."
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

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Пользователь с таким номером телефона не найден в роли '{selected_role}'.\n\nОбратитесь к администратору для добавления в систему.",
            reply_markup=get_role_selection()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id