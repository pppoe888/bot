
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from config import BOT_TOKEN, ADMIN_ID
from handlers.auth import start, handle_contact, create_admin, handle_role_selection, setup_admin_roles, handle_contact_help, handle_multi_role_selection
from keyboards import get_role_selection
from handlers.driver import driver_start, car_inspection, select_car_for_inspection, report_problem, handle_problem_report, handle_problem_description, my_shifts, back_to_menu, handle_inspection_photo
from handlers.inspection import start_inspection, confirm_start_shift, loading_cargo, load_cargo_item, ready_for_delivery
from handlers.delivery import delivery_list
from handlers.admin import (
    admin_panel, admin_employees_section, admin_cars_section, 
    admin_shifts_section, admin_reports_section, employees_stats, 
    shifts_stats, view_car_info, view_delivered_items, view_shift_details,
    view_shift_inspection, view_shift_cargo, active_shifts, 
    view_history_shift_inspection,
    view_active_shift_cargo, shifts_history,
    show_active_shift_photos
)
from handlers.admin_actions import (
    manage_drivers, manage_logists, manage_cars, show_employees_list,
    handle_add_driver, handle_add_logist, handle_add_car, handle_confirm,
    show_drivers_list, edit_driver, delete_driver, edit_driver_field,
    show_logists_list, edit_logist, delete_logist, edit_logist_field,
    show_cars_list, edit_car, delete_car, edit_car_field,
    show_active_shifts, end_shift, cancel_shift, shifts_history as admin_shifts_history,
    handle_admin_text
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

    # Очищаем только временные состояния, сохраняя важные данные
    temp_states_to_clear = ["state", "selected_car_id", "temp_shift_id", "inspection_photos", "awaiting_text_phone"]
    for key in temp_states_to_clear:
        context.user_data.pop(key, None)

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
                from handlers.driver import show_driver_menu
                await show_driver_menu(update, context, user.name)
            elif user.role == "logist":
                from keyboards import get_logist_menu
                keyboard = get_logist_menu()
                text = f"Меню логиста\n\nВыберите действие:"
                
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

    # Проверяем, ожидается ли ввод номера телефона текстом
    if context.user_data.get("awaiting_text_phone"):
        from handlers.auth import handle_text_phone_input
        context.user_data.pop("awaiting_text_phone", None)
        await handle_text_phone_input(update, context, text)
        return

    # Проверяем, ожидается ли описание проблемы
    if context.user_data.get("awaiting_problem_description"):
        await handle_problem_description(update, context)
        return

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

    # Если сообщение не распознано
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Команда не распознана. Используйте кнопки меню."
    )
    context.user_data["last_message_id"] = message.message_id

async def handle_photo_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фотографий"""
    # Проверяем, находимся ли мы в процессе осмотра
    if context.user_data.get("inspection_shift_id") and context.user_data.get("current_photo_step"):
        handled = await handle_inspection_photo(update, context)
        if handled:
            return

    # Если фото не обработано в рамках осмотра - блокируем
    await delete_previous_messages(update, context)
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ОТПРАВКА ФОТОГРАФИЙ ЗАПРЕЩЕНА!\n\nФотографии разрешены только во время осмотра автомобиля.\n\nДля отправки фото:\n1. Выберите '🔍 Осмотр автомобиля'\n2. Следуйте инструкциям\n\nИспользуйте кнопки меню для навигации."
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
        await back_to_menu(update, context)
    elif data == "delivery_list":
        await delivery_list(update, context)
    elif data == "shifts_report":
        await report(update, context)
    elif data == "parking_check":
        await parking_check(update, context)
    elif data == "report":
        await report(update, context)
    elif data == "cancel_action":
        # Очищаем только временные состояния
        temp_states_to_clear = ["state", "selected_car_id", "temp_shift_id", "inspection_photos"]
        for key in temp_states_to_clear:
            context.user_data.pop(key, None)
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

    # Обработчик фотографий (должен быть первым для корректной обработки)
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo_messages))

    # Обработчики админ панели
    application.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
    application.add_handler(CallbackQueryHandler(admin_cars_section, pattern="^admin_cars_section$"))
    application.add_handler(CallbackQueryHandler(admin_employees_section, pattern="^admin_employees_section$"))
    application.add_handler(CallbackQueryHandler(admin_shifts_section, pattern="^admin_shifts_section$"))
    application.add_handler(CallbackQueryHandler(admin_reports_section, pattern="^admin_reports_section$"))

    # Обработчик фотографий активных смен (ДОЛЖЕН БЫТЬ ПЕРЕД общими обработчиками)
    application.add_handler(CallbackQueryHandler(show_active_shift_photos, pattern="^active_photos_\\d+$"))

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

    application.add_handler(CallbackQueryHandler(edit_driver_field, pattern="^name_edit_driver_\\d+$"))
    application.add_handler(CallbackQueryHandler(edit_driver_field, pattern="^phone_edit_driver_\\d+$"))
    application.add_handler(CallbackQueryHandler(edit_logist_field, pattern="^name_edit_logist_\\d+$"))
    application.add_handler(CallbackQueryHandler(edit_logist_field, pattern="^phone_edit_logist_\\d+$"))

    application.add_handler(CallbackQueryHandler(handle_role_selection, pattern="^role_(admin|driver|logist)$"))

    # Обработчики для водителей
    application.add_handler(CallbackQueryHandler(car_inspection, pattern="^car_inspection$"))
    application.add_handler(CallbackQueryHandler(select_car_for_inspection, pattern="^select_car_\\d+$"))
    application.add_handler(CallbackQueryHandler(report_problem, pattern="^report_problem$"))
    application.add_handler(CallbackQueryHandler(handle_problem_report, pattern="^problem_"))
    application.add_handler(CallbackQueryHandler(my_shifts, pattern="^my_shifts$"))
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back_to_menu$"))

    # Callback обработчики для редактирования логистов
    application.add_handler(CallbackQueryHandler(edit_logist, pattern=r"^edit_logist_\d+$"))
    application.add_handler(CallbackQueryHandler(delete_logist, pattern=r"^delete_logist_\d+$"))
    application.add_handler(CallbackQueryHandler(edit_logist_field, pattern=r"^(name|phone)_logist_\d+$"))

    # Callback обработчики для управления сменами
    application.add_handler(CallbackQueryHandler(show_active_shifts, pattern=r"^show_active_shifts$"))
    application.add_handler(CallbackQueryHandler(end_shift, pattern=r"^end_shift_\d+$"))
    application.add_handler(CallbackQueryHandler(cancel_shift, pattern=r"^cancel_shift_\d+$"))

    # История смен
    application.add_handler(CallbackQueryHandler(admin_shifts_history, pattern="^shifts_history$"))

    # Просмотр деталей смен
    application.add_handler(CallbackQueryHandler(view_shift_details, pattern="^view_shift_\\d+$"))
    application.add_handler(CallbackQueryHandler(view_shift_inspection, pattern="^view_inspection_\\d+$"))
    application.add_handler(CallbackQueryHandler(view_shift_cargo, pattern="^view_cargo_\\d+$"))
    application.add_handler(CallbackQueryHandler(view_car_info, pattern="^view_car_info_\\d+$"))
    application.add_handler(CallbackQueryHandler(view_delivered_items, pattern="^view_delivered_\\d+$"))

    # Активные смены  
    application.add_handler(CallbackQueryHandler(show_active_shifts, pattern="^active_shifts$"))

    # Обработчики для осмотра автомобиля
    application.add_handler(CallbackQueryHandler(start_inspection, pattern="^start_inspection$"))
    application.add_handler(CallbackQueryHandler(confirm_start_shift, pattern="^confirm_start_shift$"))
    application.add_handler(CallbackQueryHandler(loading_cargo, pattern="^loading_cargo$"))
    application.add_handler(CallbackQueryHandler(load_cargo_item, pattern="^load_item_"))
    application.add_handler(CallbackQueryHandler(ready_for_delivery, pattern="^ready_for_delivery$"))

    # Обработчики inline кнопок диалога
    application.add_handler(CallbackQueryHandler(handle_dialog_callbacks, pattern="^(write_message|refresh_chat|open_chat|cancel_writing|delivery_list|shifts_report|parking_check|report|cancel_action)$"))

    # Обработчик помощи с контактом и методов ввода телефона
    application.add_handler(CallbackQueryHandler(handle_contact_help, pattern="^contact_help$"))

    # Импортируем новые обработчики
    from handlers.auth import handle_send_contact_method, handle_text_phone_method, handle_request_contact_button, handle_share_contact, handle_auth_request_contact
    application.add_handler(CallbackQueryHandler(handle_share_contact, pattern="^share_contact$"))
    application.add_handler(CallbackQueryHandler(handle_auth_request_contact, pattern="^auth_request_contact$"))
    application.add_handler(CallbackQueryHandler(handle_request_contact_button, pattern="^request_contact_button$"))
    application.add_handler(CallbackQueryHandler(handle_send_contact_method, pattern="^send_contact_method$"))
    application.add_handler(CallbackQueryHandler(handle_text_phone_method, pattern="^text_phone_method$"))

    # Обработчик кнопки назад к ролям
    application.add_handler(CallbackQueryHandler(lambda u, c: start(u, c), pattern="^back_to_roles$"))

    # Обработчик выбора роли при множественных ролях
    application.add_handler(CallbackQueryHandler(handle_multi_role_selection, pattern="^auth_role_"))

    # Обработчик кнопки назад с очисткой клавиатуры
    async def handle_back_to_start_with_cleanup(update, context):
        from telegram import ReplyKeyboardRemove
        try:
            # Убираем клавиатуру контакта если она активна
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🔄 Возвращаемся к началу...",
                reply_markup=ReplyKeyboardRemove()
            )
        except:
            pass
        await start(update, context)

    application.add_handler(CallbackQueryHandler(handle_back_to_start_with_cleanup, pattern="^back_to_start$"))

    # Обработчик всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

    # ПОЛНАЯ блокировка всех медиа файлов
    application.add_handler(MessageHandler(
        filters.VIDEO | filters.AUDIO | filters.Document.ALL | 
        filters.VOICE | filters.VIDEO_NOTE | filters.Sticker.ALL | 
        filters.ANIMATION | filters.LOCATION,
        block_all_media
    ))

    # Добавляем обработчик для просмотра фото осмотра
    application.add_handler(CallbackQueryHandler(view_shift_inspection, pattern="^view_inspection_\\d+$"))
    application.add_handler(CallbackQueryHandler(view_history_shift_inspection, pattern="^history_photos_\\d+$"))

    # Запуск бота
    print("Бот запущен!")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
