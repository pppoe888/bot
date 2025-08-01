from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, ADMIN_ID
from handlers.auth import start, handle_contact, create_admin, handle_role_selection, setup_admin_roles, handle_contact_help
from keyboards import get_role_selection
from handlers.driver import start_shift, select_car, show_route, report_problem, handle_problem_report, handle_problem_description, handle_shift_photo
from handlers.delivery import delivery_list
from handlers.admin import admin_panel, admin_cars_section, admin_employees_section, admin_shifts_section, admin_reports_section
from handlers.admin_actions import (
    handle_add_driver, handle_add_logist, handle_add_car, handle_confirm,
    show_drivers_list, edit_driver, delete_driver, edit_driver_field,
    show_logists_list, edit_logist, delete_logist, edit_logist_field,
    manage_cars, show_cars_list, edit_car, delete_car, edit_car_field,
    confirm_add_car, show_active_shifts, end_shift, cancel_shift, shifts_history,
    manage_drivers, manage_logists, show_employees_list, handle_admin_text
)
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
        from keyboards import get_admin_inline_keyboard
        keyboard = get_admin_inline_keyboard()
        text = "Администрирование"
        
        try:
            await update.callback_query.edit_message_text(text, reply_markup=keyboard)
        except:
            message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=keyboard
            )
            context.user_data["last_message_id"] = message.message_id
        return

    # Проверяем роль пользователя
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == user_id).first()

        if user:
            if user.role == "driver":
                from keyboards import get_driver_menu
                keyboard = get_driver_menu()
                text = f"Меню водителя\n\nВыберите действие:"
            elif user.role == "logist":
                from keyboards import get_logist_menu
                keyboard = get_logist_menu()
                text = f"Меню логиста\n\nВыберите действие:"
            else:
                keyboard = get_role_selection()
                text = "Выберите вашу роль:"

            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard)
            except:
                message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    reply_markup=keyboard
                )
                context.user_data["last_message_id"] = message.message_id
        else:
            await start(update, context)
    finally:
        db.close()

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка всех текстовых сообщений"""
    text = update.message.text

    # Удаляем сообщение пользователя после ввода
    await delete_previous_messages(update, context)

    # Проверяем состояние пользователя для админских функций
    current_state = context.user_data.get("state")
    if current_state == "writing_message":
        await send_message_to_chat(update, context, text)
        return
    elif current_state in [states.ADDING_DRIVER, states.ADDING_LOGIST, states.ADDING_CAR, states.EDITING_DRIVER, states.EDITING_LOGIST]:
        await handle_admin_text(update, context)
        return
    elif current_state == "problem_description":
        await handle_problem_description(update, context)
        return

    # Если сообщение не распознано
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Команда не распознана. Используйте кнопки меню."
    )
    context.user_data["last_message_id"] = message.message_id

async def block_all_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ПОЛНАЯ блокировка всех фотографий без исключений"""
    await delete_previous_messages(update, context)
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ОТПРАВКА ФОТОГРАФИЙ ПОЛНОСТЬЮ ЗАПРЕЩЕНА!\n\nВСЕ ИЗОБРАЖЕНИЯ ЗАБЛОКИРОВАНЫ:\n• Фото с камеры\n• Фото из галереи\n• Скриншоты\n• Любые картинки\n• Изображения любого типа\n\nБЕЗОПАСНОСТЬ: Передача изображений отключена администратором по соображениям безопасности.\n\nИспользуйте только текстовые сообщения и кнопки интерфейса."
    )
    context.user_data["last_message_id"] = message.message_id

async def block_all_media(update, context):
    """ПОЛНАЯ блокировка всех медиа файлов"""
    await delete_previous_messages(update, context)
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ПЕРЕДАЧА МЕДИА ПОЛНОСТЬЮ ЗАБЛОКИРОВАНА!\n\nЗАПРЕЩЕНО ВСЁ:\n• Все видео файлы\n• Все аудио записи\n• Все документы и файлы\n• Голосовые сообщения\n• Видео-сообщения\n• Стикеры и анимации\n• GIF файлы\n• Геолокация\n• Любые загрузки\n\nБЕЗОПАСНОСТЬ: Передача медиа-контента отключена администратором.\n\nИспользуйте только текстовые сообщения!"
    )
    context.user_data["last_message_id"] = message.message_id

async def cleanup_admin_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистка чата администратора (удаление последних сообщений)"""
    chat_id = update.effective_chat.id
    message_ids = context.chat_data.get("admin_message_ids", [])

    # Удаляем сообщения в обратном порядке
    for message_id in reversed(message_ids):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения {message_id}: {e}")

    # Очищаем список message_ids
    context.chat_data["admin_message_ids"] = []

async def handle_dialog_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик inline кнопок диалога"""
    query = update.callback_query
    data = query.data

    if data == "write_message":
        await write_message(update, context)
    elif data == "refresh_chat":
        await refresh_chat(update, context)
    elif data == "open_chat":
        await chat(update, context)
    elif data == "cancel_writing":
        context.user_data.pop("state", None)
        await chat(update, context)
    elif data == "back_to_menu":
        await handle_back_button(update, context)
    elif data == "start_shift":
        await start_shift(update, context)
    elif data == "show_route":
        await show_route(update, context)
    elif data == "report_problem":
        await report_problem(update, context)
    elif data == "delivery_list":
        await delivery_list(update, context)
    elif data == "shifts_report":
        await report(update, context)
    elif data == "parking_check":
        await parking_check(update, context)
    elif data == "report":
        await report(update, context)
    elif data == "cancel_action":
        context.user_data.clear()
        await handle_back_button(update, context)

    await query.answer()

def main():
    """Главная функция бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("create_admin", create_admin))
    application.add_handler(CommandHandler("setup_admin", setup_admin_roles))

    # Обработчик контактов
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # ПОЛНАЯ блокировка всех фотографий без исключений
    application.add_handler(MessageHandler(filters.PHOTO, block_all_photos))

    # Админские разделы
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(admin_cars_section, pattern="^admin_cars_section$"))
    application.add_handler(CallbackQueryHandler(admin_employees_section, pattern="^admin_employees_section$"))
    application.add_handler(CallbackQueryHandler(admin_shifts_section, pattern="^admin_shifts_section$"))
    application.add_handler(CallbackQueryHandler(admin_reports_section, pattern="^admin_reports_section$"))

    # Админские действия
    application.add_handler(CallbackQueryHandler(handle_add_driver, pattern="^add_driver$"))
    application.add_handler(CallbackQueryHandler(handle_add_logist, pattern="^add_logist$"))
    application.add_handler(CallbackQueryHandler(handle_add_car, pattern="^add_car$"))
    application.add_handler(CallbackQueryHandler(handle_confirm, pattern="^confirm$"))
    application.add_handler(CallbackQueryHandler(manage_cars, pattern="^manage_cars$"))

    # Управление сотрудниками
    application.add_handler(CallbackQueryHandler(manage_drivers, pattern="^manage_drivers$"))
    application.add_handler(CallbackQueryHandler(manage_logists, pattern="^manage_logists$"))
    application.add_handler(CallbackQueryHandler(show_employees_list, pattern="^employees_list$"))

    # Управление автомобилями
    application.add_handler(CallbackQueryHandler(lambda u, c: show_cars_list(u, c, "view"), pattern="^cars_list_view$"))
    application.add_handler(CallbackQueryHandler(lambda u, c: show_cars_list(u, c, "edit"), pattern="^cars_list_edit$"))
    application.add_handler(CallbackQueryHandler(lambda u, c: show_cars_list(u, c, "delete"), pattern="^cars_list_delete$"))
    application.add_handler(CallbackQueryHandler(edit_car, pattern="^edit_car_\\d+$"))
    application.add_handler(CallbackQueryHandler(delete_car, pattern="^delete_car_\\d+$"))
    application.add_handler(CallbackQueryHandler(edit_car_field, pattern="^(number|brand|model|fuel|mileage)_edit_\\d+$"))

    application.add_handler(CallbackQueryHandler(lambda u, c: show_drivers_list(u, c, "edit_driver"), pattern="^edit_driver_list$"))
    application.add_handler(CallbackQueryHandler(lambda u, c: show_logists_list(u, c, "edit_logist"), pattern="^edit_logist_list$"))
    application.add_handler(CallbackQueryHandler(lambda u, c: show_drivers_list(u, c, "delete_driver"), pattern="^delete_driver_list$"))
    application.add_handler(CallbackQueryHandler(lambda u, c: show_logists_list(u, c, "delete_logist"), pattern="^delete_logist_list$"))

    application.add_handler(CallbackQueryHandler(edit_driver, pattern="^edit_driver_\\d+$"))
    application.add_handler(CallbackQueryHandler(edit_logist, pattern="^edit_logist_\\d+$"))
    application.add_handler(CallbackQueryHandler(delete_driver, pattern="^delete_driver_\\d+$"))
    application.add_handler(CallbackQueryHandler(delete_logist, pattern="^delete_logist_\\d+$"))

    application.add_handler(CallbackQueryHandler(edit_driver_field, pattern="^edit_name_driver_\\d+$"))
    application.add_handler(CallbackQueryHandler(edit_driver_field, pattern="^edit_phone_driver_\\d+$"))
    application.add_handler(CallbackQueryHandler(edit_logist_field, pattern="^edit_name_logist_\\d+$"))
    application.add_handler(CallbackQueryHandler(edit_logist_field, pattern="^edit_phone_logist_\\d+$"))

    application.add_handler(CallbackQueryHandler(select_car, pattern="^select_car_"))
    application.add_handler(CallbackQueryHandler(handle_role_selection, pattern="^role_(admin|driver|logist)$"))

    # Обработчики для проблем водителей
    application.add_handler(CallbackQueryHandler(handle_problem_report, pattern="^problem_"))

    # Callback обработчики для редактирования логистов
    application.add_handler(CallbackQueryHandler(edit_logist, pattern=r"^edit_logist_\d+$"))
    application.add_handler(CallbackQueryHandler(delete_logist, pattern=r"^delete_logist_\d+$"))
    application.add_handler(CallbackQueryHandler(edit_logist_field, pattern=r"^(name|phone)_logist_\d+$"))

    # Callback обработчики для управления сменами
    application.add_handler(CallbackQueryHandler(show_active_shifts, pattern=r"^show_active_shifts$"))
    application.add_handler(CallbackQueryHandler(end_shift, pattern=r"^end_shift_\d+$"))
    application.add_handler(CallbackQueryHandler(cancel_shift, pattern=r"^cancel_shift_\d+$"))


    # Обработчики inline кнопок диалога
    application.add_handler(CallbackQueryHandler(handle_dialog_callbacks, pattern="^(write_message|refresh_chat|back_to_menu|open_chat|cancel_writing|start_shift|show_route|report_problem|delivery_list|shifts_report|parking_check|report|cancel_action)$"))

    # Обработчик помощи с контактом
    application.add_handler(CallbackQueryHandler(handle_contact_help, pattern="^contact_help$"))

    # Обработчик кнопки назад к ролям
    application.add_handler(CallbackQueryHandler(lambda u, c: start(u, c), pattern="^back_to_roles$"))

    # Обработчик всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

    # ПОЛНАЯ блокировка всех медиа файлов и изображений
    application.add_handler(MessageHandler(
        filters.VIDEO | filters.AUDIO | filters.Document.ALL | 
        filters.VOICE | filters.VIDEO_NOTE | filters.Sticker.ALL | 
        filters.ANIMATION | filters.LOCATION,
        block_all_media
    ))

    # Запуск бота
    print("Бот запущен!")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()