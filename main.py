from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
from handlers.auth import start, handle_contact, create_admin
from handlers.driver import start_shift
from handlers.delivery import delivery_list
from handlers.admin import admin_panel
from handlers.admin_actions import handle_admin_text
from handlers.chat import chat
from handlers.parking import parking_check
from handlers.report import report

async def block_media(update, context):
    """Blocks media messages and informs the user."""
    await update.message.reply_text("Отправка фото, видео и файлов запрещена!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create_admin", create_admin))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # Обработчики callback queries (inline кнопки)
    from handlers.admin import manage_drivers, manage_cars
    
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    app.add_handler(CallbackQueryHandler(manage_drivers, pattern="^manage_drivers$"))
    app.add_handler(CallbackQueryHandler(manage_cars, pattern="^manage_cars$"))
    
    # Обработчики для добавления
    async def handle_add_driver(update, context):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("👤 Введите имя водителя:")
        context.user_data["admin_action"] = "adding_driver"
        context.user_data["driver_data"] = {}
    
    async def handle_add_car(update, context):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("🚗 Введите номер машины:")
        context.user_data["admin_action"] = "adding_car"
        context.user_data["car_data"] = {}
    
    app.add_handler(CallbackQueryHandler(handle_add_driver, pattern="^add_driver$"))
    app.add_handler(CallbackQueryHandler(handle_add_car, pattern="^add_car$"))
    
    # Общий обработчик для остальных callback queries
    app.add_handler(CallbackQueryHandler(admin_panel))

    # Обработчики текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🛠️ Админка"), admin_panel))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🚛 Начать смену"), start_shift))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📦 Список доставки"), delivery_list))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("💬 Чат водителей"), chat))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🅿️ Стоянка"), parking_check))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📊 Отчёт смен"), report))

    # Блокировка фото и файлов
    app.add_handler(MessageHandler(filters.PHOTO, block_media))
    app.add_handler(MessageHandler(filters.Document.ALL, block_media))
    app.add_handler(MessageHandler(filters.VIDEO, block_media))
    app.add_handler(MessageHandler(filters.AUDIO, block_media))
    app.add_handler(MessageHandler(filters.VOICE, block_media))
    app.add_handler(MessageHandler(filters.VIDEO_NOTE, block_media))
    app.add_handler(MessageHandler(filters.Sticker.ALL, block_media))

    # Обработчик для админских действий (должен быть перед общими обработчиками)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_text))
    # Запуск бота
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()