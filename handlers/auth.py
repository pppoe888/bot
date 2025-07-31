from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, User
from keyboards import get_role_selection, get_admin_menu, get_driver_menu, get_logist_menu, get_contact_keyboard
from config import ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = update.effective_user.id

    # Проверяем, является ли пользователь администратором
    if user_id == ADMIN_ID:
        keyboard = get_role_selection()
        text = "👑 Добро пожаловать, администратор!\n\n👥 Выберите роль для входа:"
        message = await update.message.reply_text(text, reply_markup=keyboard)
        context.user_data["last_message_id"] = message.message_id
        return

    # Для всех остальных пользователей показываем меню выбора роли
    keyboard = get_role_selection()
    text = "👋 Добро пожаловать!\n\n👥 Выберите вашу роль:"
    message = await update.message.reply_text(text, reply_markup=keyboard)
    context.user_data["last_message_id"] = message.message_id

async def create_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создание администратора"""
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
        return

    await update.message.reply_text("✅ Вы уже являетесь администратором!")

async def setup_admin_roles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Настройка ролей администратора"""
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
        return

    # Получаем имя пользователя
    user_name = update.effective_user.first_name or "Администратор"
    if update.effective_user.last_name:
        user_name += f" {update.effective_user.last_name}"

    # Просим номер телефона
    message = await update.message.reply_text(
        f"📱 Отправьте ваш номер телефона для создания записей водителя и логиста.\n\n"
        f"Это позволит вам авторизоваться как водитель или логист через номер телефона.",
        reply_markup=get_contact_keyboard()
    )
    context.user_data["setup_admin"] = True
    context.user_data["last_message_id"] = message.message_id

async def handle_role_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора роли"""
    query = update.callback_query
    await query.answer()

    selected_role = query.data.replace("role_", "")
    context.user_data["selected_role"] = selected_role

    role_display = "водитель" if selected_role == "driver" else "логист"

    # Удаляем предыдущие сообщения
    try:
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )
    except:
        pass

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📱 Для авторизации как {role_display} поделитесь номером телефона:",
        reply_markup=get_contact_keyboard()
    )
    context.user_data["last_message_id"] = message.message_id

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка получения контакта для авторизации"""
    contact = update.message.contact
    phone = contact.phone_number
    user_id = update.effective_user.id

    # Проверяем, это настройка администратора
    if context.user_data.get("setup_admin") and user_id == ADMIN_ID:
        from handlers.admin_actions import create_admin_entries
        
        user_name = update.effective_user.first_name or "Администратор"
        if update.effective_user.last_name:
            user_name += f" {update.effective_user.last_name}"

        success = await create_admin_entries(phone, user_name)
        
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

        if success:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Записи администратора созданы!\n\nТеперь вы можете авторизоваться как водитель или логист через номер телефона.",
                reply_markup=get_role_selection()
            )
        else:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Ошибка создания записей администратора.",
                reply_markup=get_role_selection()
            )
            
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
        return

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