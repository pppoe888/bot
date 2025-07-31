from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, ADMIN_ID
from handlers.auth import start, handle_contact, create_admin, handle_role_selection, setup_admin_roles
from keyboards import get_role_selection, get_admin_menu, get_driver_menu, get_logist_menu, get_contact_keyboard
from handlers.driver import start_shift, select_car
from handlers.delivery import delivery_list
from handlers.admin import admin_panel, manage_drivers, manage_cars, manage_logists, admin_stats, admin_panel_text, manage_cars_text, admin_stats_text
from handlers.admin_actions import handle_admin_text, handle_add_driver, handle_add_logist, handle_add_car, handle_confirm
from handlers.chat import chat, write_message, send_message_to_chat, refresh_chat
from handlers.parking import parking_check
from handlers.report import report
import states
from database import SessionLocal, User, Car

async def delete_previous_messages(update, context):
    """Удаляет предыдущие сообщения"""
    try:
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")
    
    try:
        if update.message:
            await update.message.delete()
    except Exception as e:
        print(f"Ошибка при удалении текущего сообщения: {e}")

async def handle_back_button(update, context):
    """Обработчик кнопки Назад"""
    user_id = update.effective_user.id

    # Очищаем состояние
    context.user_data.clear()

    # Если это админ
    if user_id == ADMIN_ID:
        keyboard = get_admin_menu()
        text = "👑 Админ панель"
        message = await update.message.reply_text(text, reply_markup=keyboard)
        context.user_data["last_message_id"] = message.message_id
        return

    # Проверяем роль пользователя
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()

        if user:
            if user.role == "driver":
                keyboard = get_driver_menu()
                text = f"🚛 Меню водителя"
            elif user.role == "logist":
                keyboard = get_logist_menu()
                text = f"📋 Меню логиста"
            else:
                keyboard = get_role_selection()
                text = "Выберите вашу роль:"

            message = await update.message.reply_text(text, reply_markup=keyboard)
            context.user_data["last_message_id"] = message.message_id
        else:
            await start(update, context)
    finally:
        db.close()

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка всех текстовых сообщений"""
    text = update.message.text

    # Проверяем состояние пользователя для админских функций
    current_state = context.user_data.get("state")
    if current_state == "writing_message":
        await send_message_to_chat(update, context, text)
        return
    elif current_state in [states.ADDING_DRIVER, states.ADDING_LOGIST, states.ADDING_CAR]:
        await handle_admin_text(update, context)
        return

    # Обработка выбора роли
    if text == "👨‍💼 Администратор":
        # Проверяем, является ли пользователь админом
        if update.effective_user.id == ADMIN_ID:
            await delete_previous_messages(update, context)
            keyboard = get_admin_menu()
            text_msg = "👑 Добро пожаловать, администратор!\n\n🛠️ Админ панель"
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text_msg,
                reply_markup=keyboard
            )
            context.user_data["last_message_id"] = message.message_id
        else:
            await delete_previous_messages(update, context)
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ У вас нет прав администратора.\n\nВыберите другую роль:",
                reply_markup=get_role_selection()
            )
            context.user_data["last_message_id"] = message.message_id
        return
    elif text in ["📋 Логист", "🚛 Водитель"]:
        # Определяем выбранную роль
        selected_role = "logist" if text == "📋 Логист" else "driver"
        context.user_data["selected_role"] = selected_role
        
        role_display = "логист" if selected_role == "logist" else "водитель"
        
        # Удаляем предыдущие сообщения
        await delete_previous_messages(update, context)
        
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"📱 Для авторизации как {role_display} поделитесь номером телефона:",
            reply_markup=get_contact_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id
        return

    # Обработка кнопки "Назад"
    if text == "⬅️ Назад":
        await handle_back_button(update, context)
        return

    # Обработка меню водителя
    if text == "🚛 Начать смену":
        await start_shift(update, context)
        return
    elif text == "📦 Список поставок":
        await delivery_list(update, context)
        return
    elif text == "💬 Чат":
        await chat(update, context)
        return
    elif text == "🅿️ Парковка":
        await parking_check(update, context)
        return
    elif text == "📊 Отчет":
        await report(update, context)
        return

    # Обработка меню администратора
    if text == "👤 Управление пользователями":
        await admin_panel_text(update, context)
        return
    elif text == "🚗 Управление машинами":
        await manage_cars_text(update, context)
        return
    elif text == "📊 Статистика":
        await admin_stats_text(update, context)
        return

    # Обработка меню логиста
    if text == "📦 Список доставки":
        await delivery_list(update, context)
        return
    elif text == "💬 Чат водителей":
        await chat(update, context)
        return
    elif text == "📊 Отчёт смен":
        await report(update, context)
        return

    # Обработка чата
    if text == "✍️ Написать сообщение":
        await write_message(update, context)
        return
    elif text == "🔄 Обновить":
        await refresh_chat(update, context)
        return

    # Если сообщение не распознано
    await delete_previous_messages(update, context)
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="❌ Команда не распознана. Используйте кнопки меню."
    )
    context.user_data["last_message_id"] = message.message_id

async def block_media(update, context):
    """Блокировка медиа файлов"""
    await delete_previous_messages(update, context)
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="❌ Отправка медиа файлов запрещена. Используйте только текстовые сообщения."
    )
    context.user_data["last_message_id"] = message.message_id

def main():
    """Главная функция бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("create_admin", create_admin))
    application.add_handler(CommandHandler("setup_admin", setup_admin_roles))

    # Обработчик контактов
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # Обработчики callback queries (inline кнопки)
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(manage_drivers, pattern="^manage_drivers$"))
    application.add_handler(CallbackQueryHandler(manage_cars, pattern="^manage_cars$"))
    application.add_handler(CallbackQueryHandler(manage_logists, pattern="^manage_logists$"))
    application.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(handle_add_driver, pattern="^add_driver$"))
    application.add_handler(CallbackQueryHandler(handle_add_logist, pattern="^add_logist$"))
    application.add_handler(CallbackQueryHandler(handle_add_car, pattern="^add_car$"))
    application.add_handler(CallbackQueryHandler(handle_confirm, pattern="^confirm$"))
    application.add_handler(CallbackQueryHandler(select_car, pattern="^select_car_"))
    application.add_handler(CallbackQueryHandler(handle_role_selection, pattern="^role_"))

    # Обработчик всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

    # Блокировка медиа файлов
    application.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.Document.ALL | 
        filters.VOICE | filters.VIDEO_NOTE | filters.Sticker.ALL | filters.ANIMATION,
        block_media
    ))

    # Запуск бота
    print("🤖 Бот запущен!")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()