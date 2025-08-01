from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, User
from keyboards import get_role_selection, get_contact_inline_keyboard
from config import ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = update.effective_user.id

    # Проверяем, является ли пользователь администратором
    if user_id == ADMIN_ID:
        keyboard = get_role_selection()
        text = "Выберите вход:"
        
        if update.message:
            message = await update.message.reply_text(text, reply_markup=keyboard)
        else:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=keyboard
            )
        context.user_data["last_message_id"] = message.message_id
        return

    # Проверяем, есть ли пользователь уже в базе
    db = SessionLocal()
    try:
        # Ищем пользователя по telegram_id
        existing_user = db.query(User).filter(User.telegram_id == user_id).first()
        
        if existing_user:
            # Пользователь найден, сразу авторизуем
            user_name = existing_user.name
            user_role = existing_user.role

            # Удаляем предыдущие сообщения если есть
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

            # Отправляем приветственное сообщение с соответствующим меню
            if user_role == "driver":
                from keyboards import get_driver_dialog_keyboard
                keyboard = get_driver_dialog_keyboard()
                text = f"Добро пожаловать, {user_name}!\n\nВы автоматически авторизованы как водитель.\n\nВыберите действие:"
            elif user_role == "logist":
                from keyboards import get_logist_dialog_keyboard
                keyboard = get_logist_dialog_keyboard()
                text = f"Добро пожаловать, {user_name}!\n\nВы автоматически авторизованы как логист.\n\nВыберите действие:"
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
            return

    finally:
        db.close()

    # Для новых пользователей показываем меню выбора роли
    keyboard = get_role_selection()
    text = "Выберите вход:"
    
    if update.message:
        message = await update.message.reply_text(text, reply_markup=keyboard)
    else:
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
        if update.message:
            await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="У вас нет прав для выполнения этой команды."
            )
        return

    if update.message:
        await update.message.reply_text("Вы уже являетесь администратором!")
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы уже являетесь администратором!"
        )

async def setup_admin_roles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Настройка ролей администратора"""
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        if update.message:
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ У вас нет прав для выполнения этой команды."
            )
        return

    # Получаем имя пользователя
    user_name = update.effective_user.first_name or "Администратор"
    if update.effective_user.last_name:
        user_name += f" {update.effective_user.last_name}"

    # Просим номер телефона
    text = (f"📱 Отправьте ваш номер телефона для создания записей водителя и логиста.\n\n"
            f"Это позволит вам авторизоваться как водитель или логист через номер телефона.\n\n"
            f"💡 Для отправки контакта:\n"
            f"1️⃣ Нажмите на кнопку 📎 (скрепка)\n"
            f"2️⃣ Выберите 'Контакт'\n"
            f"3️⃣ Выберите свой контакт\n"
            f"4️⃣ Нажмите 'Отправить'")
    
    if update.message:
        message = await update.message.reply_text(text, reply_markup=get_role_selection())
    else:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=get_role_selection()
        )
    context.user_data["setup_admin"] = True
    context.user_data["last_message_id"] = message.message_id

async def handle_role_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора роли"""
    query = update.callback_query
    await query.answer()

    selected_role = query.data.replace("role_", "")
    context.user_data["selected_role"] = selected_role

    if selected_role == "admin":
        # Проверяем права администратора
        if update.effective_user.id == ADMIN_ID:
            from keyboards import get_admin_inline_keyboard
            text = "Администрирование"
            try:
                await query.edit_message_text(text=text, reply_markup=get_admin_inline_keyboard())
            except:
                message = await query.message.reply_text(text=text, reply_markup=get_admin_inline_keyboard())
                context.user_data["last_message_id"] = message.message_id
        else:
            text = "У вас нет прав администратора.\n\nВыберите другую роль:"
            try:
                await query.edit_message_text(text=text, reply_markup=get_role_selection())
            except:
                message = await query.message.reply_text(text=text, reply_markup=get_role_selection())
                context.user_data["last_message_id"] = message.message_id
        return

    role_display = "водитель" if selected_role == "driver" else "логист"

    text = f"Для авторизации как {role_display} поделитесь номером телефона:\n\nНажмите на кнопку ниже, чтобы узнать как поделиться контактом"
    
    try:
        await query.edit_message_text(text=text, reply_markup=get_contact_inline_keyboard())
    except:
        message = await query.message.reply_text(text=text, reply_markup=get_contact_inline_keyboard())
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

    # Нормализуем номер телефона - получаем только цифры
    phone_digits = ''.join(filter(str.isdigit, phone))
    
    # Ищем пользователя по точному совпадению номера телефона и роли
    user = db.query(User).filter(
        User.phone == phone, 
        User.role == selected_role
    ).first()
    
    # Если не найден, пробуем поиск по нормализованным номерам
    if not user:
        users_with_role = db.query(User).filter(User.role == selected_role).all()
        for u in users_with_role:
            # Получаем только цифры из номера в базе
            u_phone_digits = ''.join(filter(str.isdigit, u.phone))
            
            # Сравниваем только цифры
            if u_phone_digits == phone_digits:
                user = u
                break

    if user:
        # Пользователь найден, проверяем и обновляем telegram_id только если нужно
        if user.telegram_id != user_id:
            # Проверяем, нет ли уже пользователя с таким telegram_id
            existing_user = db.query(User).filter(User.telegram_id == user_id).first()
            if existing_user and existing_user.id != user.id:
                # Если есть другой пользователь с таким telegram_id, очищаем его
                existing_user.telegram_id = None
                db.commit()
            
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

        # Отправляем приветственное сообщение с inline меню
        if user_role == "driver":
            from keyboards import get_driver_dialog_keyboard
            keyboard = get_driver_dialog_keyboard()
            text = f"Добро пожаловать, {user_name}!\n\nВы успешно авторизованы как водитель.\n\nВыберите действие:"
        elif user_role == "logist":
            from keyboards import get_logist_dialog_keyboard
            keyboard = get_logist_dialog_keyboard()
            text = f"Добро пожаловать, {user_name}!\n\nВы успешно авторизованы как логист.\n\nВыберите действие:"
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

        # Показываем отладочную информацию для диагностики
        role_display = "водитель" if selected_role == "driver" else "логист"
        debug_users = db.query(User).filter(User.role == selected_role).all()
        
        debug_text = f"❌ Пользователь с номером {phone} не найден в роли '{role_display}'.\n\n"
        
        if debug_users:
            debug_text += f"📋 Найдено {len(debug_users)} пользователей с ролью '{role_display}':\n"
            for debug_user in debug_users[:5]:  # Показываем только первых 5
                debug_text += f"• {debug_user.name} ({debug_user.phone})\n"
            if len(debug_users) > 5:
                debug_text += f"... и еще {len(debug_users) - 5} пользователей\n"
        else:
            debug_text += f"📋 Пользователи с ролью '{role_display}' не найдены в системе.\n"
        
        debug_text += f"\n💡 Обратитесь к администратору для добавления в систему или проверки номера телефона."

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=debug_text,
            reply_markup=get_role_selection()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id

def get_contact_instruction_keyboard():
    """Клавиатура с инструкциями по контакту"""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_roles")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def handle_contact_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает инструкции по отправке контакта"""
    query = update.callback_query
    await query.answer()
    
    text = """📱 Как поделиться номером телефона:

1️⃣ Нажмите на кнопку 📎 (скрепка) в поле ввода сообщения
2️⃣ Выберите "Контакт" 
3️⃣ Выберите свой контакт из списка
4️⃣ Нажмите "Отправить"

⚠️ ВАЖНО: После отправки контакта система автоматически найдет вас в базе и авторизует."""
    
    try:
        await query.edit_message_text(text=text, reply_markup=get_contact_instruction_keyboard())
    except:
        message = await query.message.reply_text(text=text, reply_markup=get_contact_instruction_keyboard())
        context.user_data["last_message_id"] = message.message_id
