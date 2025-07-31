from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from database import SessionLocal, User
from keyboards import get_driver_menu, get_admin_menu, get_phone_button
from states import WAITING_PHONE

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import ADMIN_ID

    db = SessionLocal()
    
    try:
        # Сначала проверяем, является ли пользователь админом
        if update.effective_user.id == ADMIN_ID:
            # Проверяем, есть ли админ в базе
            admin_user = db.query(User).filter(User.telegram_id == ADMIN_ID).first()
            
            if not admin_user:
                # Создаем админа автоматически
                admin_user = User(
                    telegram_id=ADMIN_ID,
                    phone="admin",
                    name=update.effective_user.first_name or "Администратор",
                    role="admin"
                )
                db.add(admin_user)
                db.commit()
            
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
                text=f"Добро пожаловать, Администратор {admin_user.name}!",
                reply_markup=get_admin_menu()
            )
            context.user_data.clear()
            context.user_data["last_message_id"] = message.message_id
            
        else:
            # Это не админ - проверяем авторизацию водителя
            user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()
            
            if user and user.role == "driver":
                # Удаляем предыдущее сообщение если возможно
                try:
                    await update.message.delete()
                except:
                    pass
                    
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Добро пожаловать, {user.name}!",
                    reply_markup=get_driver_menu()
                )
                context.user_data["last_message_id"] = message.message_id
                context.user_data.clear()
            else:
                # Удаляем предыдущее сообщение если возможно
                try:
                    await update.message.delete()
                except:
                    pass
                    
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Добро пожаловать! Для авторизации водителя отправьте ваш номер телефона:",
                    reply_markup=get_phone_button()
                )
                context.user_data["last_message_id"] = message.message_id
                context.user_data["state"] = WAITING_PHONE
            
    except Exception as e:
        print(f"Ошибка в start: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")
    finally:
        db.close()

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import ADMIN_ID
    
    # Админ не должен авторизовываться через номер телефона
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("❌ Администратор не может авторизоваться как водитель.")
        return

    contact = update.message.contact
    phone = contact.phone_number
    user_id = update.effective_user.id

    db = SessionLocal()

    # Ищем водителя по номеру телефона
    user = db.query(User).filter(User.phone == phone, User.role == "driver").first()

    if user:
        # Водитель найден, обновляем telegram_id
        user.telegram_id = user_id
        db.commit()

        # Получаем имя пользователя до закрытия сессии
        user_name = user.name
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
            text=f"✅ Авторизация завершена! Добро пожаловать, {user_name}!",
            reply_markup=get_driver_menu()
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data.clear()
    else:
        db.close()
        # Удаляем предыдущее сообщение
        try:
            await update.message.delete()
        except:
            pass
        
        from keyboards import get_back_keyboard
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Ваш номер не найден среди водителей. Обратитесь к администратору для добавления в систему.",
            reply_markup=get_back_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

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