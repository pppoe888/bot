from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database import SessionLocal, User
from keyboards import get_role_selection, get_contact_inline_keyboard
from config import ADMIN_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start с автоматической авторизацией"""
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

    # Проверяем, есть ли пользователь уже в базе по telegram_id
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
                from keyboards import get_driver_menu
                keyboard = get_driver_menu()
                text = f"Добро пожаловать, {user_name}!\n\nВыберите действие:"
            elif user_role == "logist":
                from keyboards import get_logist_menu
                keyboard = get_logist_menu()
                text = f"Добро пожаловать, {user_name}!\n\nВыберите действие:"
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

        # Дополнительная проверка - может пользователь есть в базе, но не привязан к telegram_id
        username = update.effective_user.first_name or "Пользователь"
        if update.effective_user.last_name:
            username += f" {update.effective_user.last_name}"

        # Ищем пользователя по имени (для диагностики)
        users_by_name = db.query(User).filter(User.name.like(f"%{username.split()[0]}%")).all()

        if users_by_name:
            # Найдены пользователи с похожим именем - возможно нужна привязка
            unlinked_users = [u for u in users_by_name if not u.telegram_id]
            if unlinked_users:
                text = f"👋 {username}!\n\n"
                text += f"Найдены непривязанные аккаунты:\n"
                for u in unlinked_users:
                    text += f"• {u.name} ({u.role})\n"
                text += f"\n💡 Для привязки аккаунта поделитесь контактом:"

                # Автоматически переходим к запросу контакта
                from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

                contact_keyboard = ReplyKeyboardMarkup(
                    [[KeyboardButton("📞 Поделиться контактом", request_contact=True)]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )

                inline_keyboard = [
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]
                ]
                inline_reply_markup = InlineKeyboardMarkup(inline_keyboard)

                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    reply_markup=inline_reply_markup
                )
                context.user_data["last_message_id"] = message.message_id

                contact_message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="👇 Нажмите кнопку для отправки контакта:",
                    reply_markup=contact_keyboard
                )
                context.user_data["contact_message_id"] = contact_message.message_id
                return

    finally:
        db.close()

    # Для новых пользователей автоматически запрашиваем контакт
    from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

    # Создаем клавиатуру с кнопкой контакта
    contact_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📞 Поделиться контактом", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    # Inline кнопка назад
    inline_keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]
    ]
    inline_reply_markup = InlineKeyboardMarkup(inline_keyboard)

    # Отправляем сообщение с просьбой поделиться контактом
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Поделитесь контактом для авторизации",
        reply_markup=inline_reply_markup
    )
    context.user_data["last_message_id"] = message.message_id

    # Отправляем сообщение с кнопкой контакта
    contact_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👇 Нажмите кнопку для отправки контакта:",
        reply_markup=contact_keyboard
    )
    context.user_data["contact_message_id"] = contact_message.message_id

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

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы уже являетесь администратором!"
    )

async def setup_admin_roles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Настройка ролей администратора"""
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
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

    # Универсальная отправка для всех клиентов
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

    from telegram import InlineKeyboardMarkup, InlineKeyboardButton

    # Inline кнопка для запроса контакта
    keyboard = [[
        InlineKeyboardButton("📞 Поделиться контактом", callback_data="auth_request_contact")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.edit_message_text("Нажмите кнопку для авторизации:", reply_markup=reply_markup)
    except:
        message = await query.message.reply_text("Нажмите кнопку для авторизации:", reply_markup=reply_markup)
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

        # Удаляем предыдущие сообщения и убираем кнопку контакта
        try:
            if context.user_data.get("last_message_id"):
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data["last_message_id"]
                )
            if context.user_data.get("contact_message_id"):
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data["contact_message_id"]
                )
            await update.message.delete()
        except:
            pass

        # Убираем клавиатуру контакта
        from telegram import ReplyKeyboardRemove
        remove_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⏳ Обрабатываем ваш контакт...",
            reply_markup=ReplyKeyboardRemove()
        )
        # Удаляем сообщение об обработке
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=remove_message.message_id
            )
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

    # Упрощенная авторизация - если есть выбранная роль, используем её
    if context.user_data.get("selected_role"):
        selected_role = context.user_data.get("selected_role")
        await authorize_by_phone_and_role(update, context, phone, user_id, selected_role)
        return

    # Автоматическая авторизация: ищем все роли пользователя по номеру телефона
    db = SessionLocal()
    try:
        # Нормализуем номер телефона - получаем только цифры
        phone_digits = ''.join(filter(str.isdigit, phone))

        # Ищем всех пользователей с этим номером телефона
        users_by_phone = []

        # Поиск по точному совпадению
        exact_matches = db.query(User).filter(User.phone == phone).all()
        users_by_phone.extend(exact_matches)

        # Если нет точных совпадений, ищем по нормализованным номерам
        if not users_by_phone:
            all_users = db.query(User).all()
            for u in all_users:
                u_phone_digits = ''.join(filter(str.isdigit, u.phone))
                if u_phone_digits == phone_digits:
                    users_by_phone.append(u)

        # Удаляем предыдущие сообщения и убираем кнопку контакта
        try:
            if context.user_data.get("last_message_id"):
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data["last_message_id"]
                )
            if context.user_data.get("contact_message_id"):
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data["contact_message_id"]
                )
            await update.message.delete()
        except:
            pass

        # Убираем клавиатуру контакта
        from telegram import ReplyKeyboardRemove
        remove_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⏳ Обрабатываем ваш контакт...",
            reply_markup=ReplyKeyboardRemove()
        )
        # Удаляем сообщение об обработке
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=remove_message.message_id
            )
        except:
            pass

        if not users_by_phone:
            # Подробная диагностика для администратора
            from config import ADMIN_ID
            if user_id == ADMIN_ID:
                try:
                    # Отправляем детальную информацию администратору
                    debug_text = f"🔍 ДИАГНОСТИКА АВТОРИЗАЦИИ\n\n"
                    debug_text += f"Номер телефона: {phone}\n"
                    debug_text += f"Нормализованный: {phone_digits}\n"
                    debug_text += f"Telegram ID: {user_id}\n\n"

                    # Показываем все номера в базе для сравнения
                    all_users = db.query(User).all()
                    debug_text += f"Всего пользователей в базе: {len(all_users)}\n\n"
                    debug_text += "Номера в базе:\n"
                    for u in all_users[:10]:  # Показываем первые 10
                        u_phone_digits = ''.join(filter(str.isdigit, u.phone))
                        debug_text += f"• {u.name}: {u.phone} ({u_phone_digits})\n"

                    await context.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=debug_text
                    )
                except:
                    pass

            # Пользователь не найден - обратиться к администратору
            from telegram import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = [
                [InlineKeyboardButton("🔄 Попробовать снова", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Пользователь с номером {phone} не найден в системе.\n\n💡 Обратитесь к администратору для добавления в систему.",
                reply_markup=reply_markup
            )
            context.user_data.clear()
            context.user_data["last_message_id"] = message.message_id
            return

        if len(users_by_phone) == 1:
            # Одна роль - автоматически авторизуем
            user = users_by_phone[0]
            await authorize_user(update, context, user, user_id)
        else:
            # Несколько ролей - предоставляем выбор
            from telegram import InlineKeyboardMarkup, InlineKeyboardButton

            keyboard = []
            for user in users_by_phone:
                role_display = "Водитель" if user.role == "driver" else "Логист" if user.role == "logist" else "Администратор"
                keyboard.append([InlineKeyboardButton(
                    f"{role_display} ({user.name})",
                    callback_data=f"auth_role_{user.role}_{user.id}"
                )])

            keyboard.append([InlineKeyboardButton("🔄 Попробовать снова", callback_data="back_to_start")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"📱 Найдено несколько ролей для номера {phone}:\n\nВыберите роль для авторизации:",
                reply_markup=reply_markup
            )
            context.user_data["last_message_id"] = message.message_id
            context.user_data["users_by_phone"] = {str(user.id): user for user in users_by_phone}

            # Сохраняем telegram_id для всех найденных пользователей с этим номером
            for user in users_by_phone:
                if user.telegram_id != user_id:
                    # Убираем telegram_id у других пользователей с таким же ID
                    existing_user = db.query(User).filter(User.telegram_id == user_id).first()
                    if existing_user and existing_user.id != user.id:
                        existing_user.telegram_id = None

                    user.telegram_id = user_id
            db.commit()

    finally:
        db.close()

async def authorize_by_phone_and_role(update: Update, context: ContextTypes.DEFAULT_TYPE, phone: str, user_id: int, selected_role: str):
    """Авторизация по номеру телефона и выбранной роли"""
    db = SessionLocal()
    try:
        # Нормализуем номер телефона
        phone_digits = ''.join(filter(str.isdigit, phone))

        # Ищем пользователя по номеру и роли
        user = db.query(User).filter(User.phone == phone, User.role == selected_role).first()

        if not user:
            users_with_role = db.query(User).filter(User.role == selected_role).all()
            for u in users_with_role:
                u_phone_digits = ''.join(filter(str.isdigit, u.phone))
                if u_phone_digits == phone_digits:
                    user = u
                    break

        # Удаляем предыдущие сообщения и убираем кнопку контакта
        try:
            if context.user_data.get("last_message_id"):
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data["last_message_id"]
                )
            if context.user_data.get("contact_message_id"):
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data["contact_message_id"]
                )
            await update.message.delete()
        except:
            pass

        # Убираем клавиатуру контакта
        from telegram import ReplyKeyboardRemove
        remove_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⏳ Обрабатываем ваш контакт...",
            reply_markup=ReplyKeyboardRemove()
        )
        # Удаляем сообщение об обработке
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=remove_message.message_id
            )
        except:
            pass

        if user:
            await authorize_user(update, context, user, user_id)
        else:
            role_display = "водитель" if selected_role == "driver" else "логист"
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Пользователь с номером {phone} не найден в роли '{role_display}'.\n\n💡 Обратитесь к администратору для добавления в систему.",
                reply_markup=get_role_selection()
            )
            context.user_data.clear()
            context.user_data["last_message_id"] = message.message_id

    finally:
        db.close()

async def authorize_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user, user_id: int):
    """Авторизация пользователя"""
    db = SessionLocal()
    try:
        # Обновляем telegram_id если нужно
        if user.telegram_id != user_id:
            # Убираем telegram_id у других пользователей с таким же telegram_id
            existing_user = db.query(User).filter(User.telegram_id == user_id).first()
            if existing_user and existing_user.id != user.id:
                existing_user.telegram_id = None
                db.commit()

            # Устанавливаем telegram_id для текущего пользователя
            user.telegram_id = user_id
            db.commit()

            # Логируем успешное сохранение
            print(f"✅ Telegram ID {user_id} сохранен для пользователя {user.name} (ID: {user.id})")

        user_name = user.name
        user_role = user.role

        # Отправляем приветственное сообщение
        if user_role == "driver":
            from handlers.driver import show_driver_menu
            context.user_data.clear()
            await show_driver_menu(update, context, user_name)
            return
        elif user_role == "logist":
            from keyboards import get_logist_menu
            keyboard = get_logist_menu()
            text = f"Добро пожаловать, {user_name}!\n\nВыберите действие:"
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

    finally:
        db.close()

def get_contact_instruction_keyboard():
    """Клавиатура с инструкциями по контакту"""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_roles")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def handle_auth_request_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик inline кнопки авторизации через контакт"""
    query = update.callback_query
    await query.answer()

    # Убираем inline-кнопку
    await query.edit_message_text("Отправьте свой контакт, нажав на кнопку ниже:")

    # Показываем reply-клавиатуру с запросом контакта
    from telegram import ReplyKeyboardMarkup, KeyboardButton

    kb = [[KeyboardButton("📱 Отправить контакт", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)

    contact_message = await query.message.reply_text("👇 Нажмите кнопку для отправки контакта:", reply_markup=reply_markup)
    context.user_data["contact_message_id"] = contact_message.message_id

async def handle_request_contact_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает кнопку для отправки контакта"""
    query = update.callback_query
    await query.answer()

    from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

    # Создаем клавиатуру с кнопкой контакта
    contact_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📞 Поделиться контактом", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    # Только кнопка назад
    inline_keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]
    ]
    inline_reply_markup = InlineKeyboardMarkup(inline_keyboard)

    try:
        # Редактируем сообщение с простым текстом
        await query.edit_message_text(text="Поделитесь контактом для авторизации", reply_markup=inline_reply_markup)

        # Отправляем сообщение с кнопкой контакта
        contact_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="👇 Нажмите кнопку для отправки контакта:",
            reply_markup=contact_keyboard
        )
        context.user_data["contact_message_id"] = contact_message.message_id
    except:
        message = await query.message.reply_text(text="Поделитесь контактом для авторизации", reply_markup=inline_reply_markup)
        context.user_data["last_message_id"] = message.message_id

        # Отправляем сообщение с кнопкой контакта
        contact_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="👇 Нажмите кнопку для отправки контакта:",
            reply_markup=contact_keyboard
        )
        context.user_data["contact_message_id"] = contact_message.message_id

async def handle_send_contact_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает инструкции по отправке контакта"""
    query = update.callback_query
    await query.answer()

    text = """📱 Как поделиться номером телефона:

1️⃣ Нажмите на кнопку 📎 (скрепка) в поле ввода сообщения
2️⃣ Выберите "Контакт" 
3️⃣ Выберите свой контакт из списка
4️⃣ Нажмите "Отправить"

⚠️ ВАЖНО: После отправки контакта система автоматически найдет вас в базе и авторизует."""

    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = [
        [InlineKeyboardButton("📞 Отправить контакт", callback_data="request_contact_button")],
        [InlineKeyboardButton("✏️ Ввести номер текстом", callback_data="text_phone_method")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    except:
        message = await query.message.reply_text(text=text, reply_markup=reply_markup)
        context.user_data["last_message_id"] = message.message_id

async def handle_text_phone_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрашивает ввод номера телефона текстом"""
    query = update.callback_query
    await query.answer()

    text = """✏️ Введите ваш номер телефона:

Примеры форматов:
• +7 900 123 45 67
• 8 900 123 45 67  
• 79001234567

📝 Просто напишите номер в любом удобном формате"""

    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = [
        [InlineKeyboardButton("📞 Отправить контакт", callback_data="send_contact_method")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    except:
        message = await query.message.reply_text(text=text, reply_markup=reply_markup)
        context.user_data["last_message_id"] = message.message_id

    context.user_data["awaiting_text_phone"] = True

async def handle_share_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик inline кнопки поделиться контактом"""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton

    text = ("📱 Как поделиться контактом:\n\n"
           "🔹 Способ 1 - Через кнопку:\n"
           "1️⃣ Нажмите 'Отправить контакт'\n"
           "2️⃣ Подтвердите отправку\n\n"
           "🔹 Способ 2 - Через меню:\n"
           "1️⃣ Нажмите на скрепку 📎\n"
           "2️⃣ Выберите 'Контакт'\n"
           "3️⃣ Выберите свой контакт\n"
           "4️⃣ Отправьте\n\n"
           "🔹 Способ 3 - Ввести номер:\n"
           "Нажмите 'Ввести номер' и введите телефон в формате +79xxxxxxxxx")

    keyboard = [
        [InlineKeyboardButton("📞 Отправить контакт", callback_data="send_contact_method")],
        [InlineKeyboardButton("✏️ Ввести номер", callback_data="text_phone_method")],
        [InlineKeyboardButton("🔙 Назад", callback_data="role_driver")]
    ]

    from telegram import InlineKeyboardMarkup

    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data["last_message_id"] = message.message_id

    await update.callback_query.answer()

async def handle_contact_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь с отправкой контакта"""
    await handle_share_contact(update, context)

async def handle_text_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE, phone_text: str):
    """Обработка текстового ввода номера телефона"""
    # Удаляем предыдущие сообщения и убираем кнопку контакта
    try:
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )
        if context.user_data.get("contact_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["contact_message_id"]
            )
        await update.message.delete()
    except:
        pass

    # Убираем клавиатуру контакта
    from telegram import ReplyKeyboardRemove
    remove_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="⏳ Обрабатываем ваш контакт...",
        reply_markup=ReplyKeyboardRemove()
    )
    # Удаляем сообщение об обработке
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=remove_message.message_id
        )
    except:
        pass

    # Нормализуем номер телефона - убираем все кроме цифр
    phone_digits = ''.join(filter(str.isdigit, phone_text))

    # Проверяем, что номер содержит достаточно цифр
    if len(phone_digits) < 10:
        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = [
            [InlineKeyboardButton("✏️ Попробовать снова", callback_data="text_phone_method")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Некорректный номер телефона!\n\nПожалуйста, введите корректный номер телефона (не менее 10 цифр).",
            reply_markup=reply_markup
        )
        context.user_data["last_message_id"] = message.message_id
        return

    # Формируем стандартизированный номер
    if phone_digits.startswith('8') and len(phone_digits) == 11:
        # Российский номер, начинающийся с 8
        formatted_phone = '+7' + phone_digits[1:]
    elif phone_digits.startswith('7') and len(phone_digits) == 11:
        # Российский номер, начинающийся с 7
        formatted_phone = '+' + phone_digits
    else:
        # Другие форматы - добавляем + если его нет
        formatted_phone = '+' + phone_digits if not phone_text.startswith('+') else phone_text

    user_id = update.effective_user.id

    # Создаем фейковый объект контакта для совместимости с существующей логикой
    class FakeContact:
        def __init__(self, phone_number):
            self.phone_number = formatted_phone

    # Временно создаем фейковое сообщение с контактом
    original_contact = update.message.contact if hasattr(update.message, 'contact') else None
    update.message.contact = FakeContact(formatted_phone)

    # Используем существующую логику обработки контакта
    await handle_contact(update, context)

    # Восстанавливаем оригинальный контакт
    if hasattr(update.message, 'contact'):
        update.message.contact = original_contact

async def handle_multi_role_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора роли при множественных ролях"""
    query = update.callback_query
    await query.answer()

    # Парсим данные callback
    data_parts = query.data.split("_")
    if len(data_parts) >= 4:
        user_id_str = data_parts[3]
        users_by_phone = context.user_data.get("users_by_phone", {})

        if user_id_str in users_by_phone:
            selected_user = users_by_phone[user_id_str]
            telegram_id = update.effective_user.id

            # Сохраняем telegram_id сразу при выборе роли
            db = SessionLocal()
            try:
                # Убираем telegram_id у других пользователей с таким же telegram_id
                existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
                if existing_user and existing_user.id != selected_user.id:
                    existing_user.telegram_id = None
                    db.commit()

                # Устанавливаем telegram_id для выбранного пользователя
                selected_user.telegram_id = telegram_id
                db.commit()

                print(f"✅ Telegram ID {telegram_id} сохранен для выбранного пользователя {selected_user.name} (ID: {selected_user.id})")
            finally:
                db.close()

            await authorize_user(update, context, selected_user, telegram_id)