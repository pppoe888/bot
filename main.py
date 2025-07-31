from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
from handlers.auth import start, handle_contact, create_admin, handle_role_selection
from keyboards import get_role_selection, get_admin_menu
from handlers.driver import start_shift, select_car
from handlers.delivery import delivery_list
from handlers.admin import admin_panel, manage_drivers, manage_cars, manage_logists, admin_stats
from handlers.admin_actions import handle_admin_text, handle_add_driver, handle_add_logist, handle_add_car, handle_confirm
from handlers.chat import chat, write_message, send_message_to_chat, refresh_chat
from handlers.parking import parking_check
from handlers.report import report
from states import WAITING_ROLE_SELECTION
from database import SessionLocal, User, Car

async def delete_previous_messages(update, context):
    """Удаляет предыдущие сообщения"""
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

async def handle_back_button(update, context):
    """Обработчик кнопки Назад"""
    from keyboards import get_driver_menu, get_logist_menu

    # Очищаем состояние пользователя
    context.user_data.clear()

    # Получаем роль пользователя
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

    if user:
        if user.role == "admin":
            keyboard = get_admin_menu()
            text = "🛠️ Админ панель"
        elif user.role == "driver":
            keyboard = get_driver_menu()
            text = "🚛 Меню водителя"
        elif user.role == "logist":
            keyboard = get_logist_menu()
            text = "📋 Меню логиста"
        else:
            keyboard = get_role_selection()
            text = "Выберите вашу роль:"
    else:
        keyboard = get_role_selection()
        text = "Выберите вашу роль:"

    db.close()

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboard
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
    app = Application.builder().token(BOT_TOKEN).build()

    # Обработчики команд (в первую очередь)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_admin", create_admin))

    # Обработчик контактов
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # Обработчики callback queries (inline кнопки)
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    app.add_handler(CallbackQueryHandler(manage_drivers, pattern="^manage_drivers$"))
    app.add_handler(CallbackQueryHandler(manage_cars, pattern="^manage_cars$"))
    app.add_handler(CallbackQueryHandler(manage_logists, pattern="^manage_logists$"))
    app.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(handle_add_driver, pattern="^add_driver$"))
    app.add_handler(CallbackQueryHandler(handle_add_logist, pattern="^add_logist$"))
    app.add_handler(CallbackQueryHandler(handle_add_car, pattern="^add_car$"))
    app.add_handler(CallbackQueryHandler(handle_confirm, pattern="^confirm$"))
    app.add_handler(CallbackQueryHandler(handle_back_button, pattern="^back_to_menu$"))

    # Обработчик выбора машины
    app.add_handler(CallbackQueryHandler(select_car, pattern="^select_car_"))

    # Обработчик для выбора роли
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex("^(👨‍💼 Администратор|📋 Логист|🚛 Водитель)$"), 
        handle_role_selection
    ))

    # Обработчики текстовых сообщений с кнопками меню (должны быть перед админскими действиями)
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🛠️ Админка"), admin_panel))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🚛 Начать смену"), start_shift))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📦 Список поставок"), delivery_list))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("💬 Чат"), chat))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🅿️ Парковка"), parking_check))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📊 Отчет"), report))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("⬅️ Назад"), handle_back_button))

    # Обработчик для админских действий (должен быть после кнопок меню)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🛠️|🚛|📦|💬|🅿️|📊|⬅️|✅|❌|✍️|🔄|👨‍💼|📋)") & ~filters.Regex("^(Водитель|Логист|Администратор)"), 
        handle_admin_text
    ))

    # Обработчики чата
    app.add_handler(CallbackQueryHandler(write_message, pattern="^write_message$"))
    app.add_handler(CallbackQueryHandler(send_message_to_chat, pattern="^send_to_chat$"))
    app.add_handler(CallbackQueryHandler(refresh_chat, pattern="^refresh_chat$"))

    # Блокировка медиа
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.Document.ALL | filters.Sticker.ALL, block_media))

    app.run_polling()

if __name__ == "__main__":
    main()