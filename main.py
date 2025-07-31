from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
from handlers.auth import start, handle_contact, create_admin
from handlers.driver import start_shift
from handlers.delivery import delivery_list
from handlers.admin import admin_panel, manage_drivers, manage_cars
from handlers.admin_actions import handle_admin_text, handle_add_driver, handle_add_car
from handlers.chat import chat, write_message, send_message_to_chat, refresh_chat
from handlers.parking import parking_check
from handlers.report import report

async def delete_previous_messages(update, context):
    """Удаляет предыдущие сообщения для очистки чата"""
    try:
        # Удаляем последнее сохраненное сообщение бота
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )
        
        # Удаляем сообщение пользователя
        if update.message:
            await update.message.delete()
        
        # Удаляем несколько предыдущих сообщений (последние 5)
        message_ids_to_delete = context.user_data.get("message_history", [])
        for msg_id in message_ids_to_delete[-5:]:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=msg_id
                )
            except:
                continue
        
        # Очищаем историю сообщений
        context.user_data["message_history"] = []
        
    except Exception as e:
        # Если не удается удалить, просто продолжаем
        pass

async def save_message_to_history(context, message_id):
    """Сохраняет ID сообщения в историю для последующего удаления"""
    if "message_history" not in context.user_data:
        context.user_data["message_history"] = []
    
    context.user_data["message_history"].append(message_id)
    
    # Ограничиваем историю последними 10 сообщениями
    if len(context.user_data["message_history"]) > 10:
        context.user_data["message_history"] = context.user_data["message_history"][-10:]

async def block_media(update, context):
    """Блокирует медиа сообщения и информирует пользователя."""
    await delete_previous_messages(update, context)
    message = await update.message.reply_text("Отправка фото, видео и файлов запрещена!")
    context.user_data["last_message_id"] = message.message_id

async def handle_back_button(update, context):
    """Обработчик кнопки 'Назад'"""
    from config import ADMIN_ID
    from keyboards import get_admin_menu, get_driver_menu
    
    # Удаляем предыдущие сообщения
    await delete_previous_messages(update, context)
    
    # Очищаем состояние и возвращаемся в главное меню
    context.user_data.clear()
    
    if update.effective_user.id == ADMIN_ID:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🛠️ Админ панель",
            reply_markup=get_admin_menu()
        )
    else:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📱 Главное меню",
            reply_markup=get_driver_menu()
        )
    
    context.user_data["last_message_id"] = message.message_id

async def handle_confirm_button(update, context):
    """Обработчик кнопки 'Подтвердить'"""
    admin_action = context.user_data.get("admin_action")
    
    if admin_action == "adding_driver":
        await confirm_add_driver(update, context)
    elif admin_action == "adding_car":
        await confirm_add_car(update, context)
    else:
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Нет действия для подтверждения"
        )
        context.user_data["last_message_id"] = message.message_id

async def handle_cancel_button(update, context):
    """Обработчик кнопки 'Отменить'"""
    from config import ADMIN_ID
    from keyboards import get_admin_menu, get_driver_menu
    
    # Удаляем сообщения
    await delete_previous_messages(update, context)
    
    context.user_data.clear()
    
    if update.effective_user.id == ADMIN_ID:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Действие отменено",
            reply_markup=get_admin_menu()
        )
    else:
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Действие отменено",
            reply_markup=get_driver_menu()
        )
    
    context.user_data["last_message_id"] = message.message_id

async def confirm_add_driver(update, context):
    """Подтверждение добавления водителя"""
    from database import SessionLocal, User
    from keyboards import get_admin_menu
    
    driver_data = context.user_data.get("driver_data", {})
    
    if not driver_data.get("name") or not driver_data.get("phone"):
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Не все данные введены"
        )
        context.user_data["last_message_id"] = message.message_id
        return
    
    db = SessionLocal()
    try:
        new_driver = User(
            name=driver_data["name"],
            phone=driver_data["phone"],
            role="driver"
        )
        db.add(new_driver)
        db.commit()
        
        # Удаляем сообщения
        await delete_previous_messages(update, context)
        
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Водитель {driver_data['name']} успешно добавлен!",
            reply_markup=get_admin_menu()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
        
    except Exception as e:
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка при добавлении: {e}"
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

async def confirm_add_car(update, context):
    """Подтверждение добавления машины"""
    from database import SessionLocal, Car
    from keyboards import get_admin_menu
    
    car_data = context.user_data.get("car_data", {})
    
    if not car_data.get("number"):
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Номер машины не введен"
        )
        context.user_data["last_message_id"] = message.message_id
        return
    
    db = SessionLocal()
    try:
        new_car = Car(
            number=car_data["number"],
            model=car_data.get("model", "")
        )
        db.add(new_car)
        db.commit()
        
        # Удаляем сообщения
        await delete_previous_messages(update, context)
        
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Машина {car_data['number']} успешно добавлена!",
            reply_markup=get_admin_menu()
        )
        context.user_data.clear()
        context.user_data["last_message_id"] = message.message_id
        
    except Exception as e:
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Ошибка при добавлении: {e}"
        )
        context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

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
    app.add_handler(CallbackQueryHandler(handle_add_driver, pattern="^add_driver$"))
    app.add_handler(CallbackQueryHandler(handle_add_car, pattern="^add_car$"))
    
    # Общий обработчик для остальных callback queries
    app.add_handler(CallbackQueryHandler(admin_panel))

    # Обработчики навигационных кнопок (должны быть первыми)
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("⬅️ Назад"), handle_back_button))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("✅ Подтвердить"), handle_confirm_button))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("❌ Отменить"), handle_cancel_button))

    # Обработчик для сообщений чата (только когда пользователь в состоянии написания сообщения)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🛠️|🚛|📦|💬|🅿️|📊|⬅️|✅|❌|✍️|🔄)"), send_message_to_chat))

    # Обработчик для админских действий
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🛠️|🚛|📦|💬|🅿️|📊|⬅️|✅|❌|✍️|🔄)"), handle_admin_text))

    # Обработчики текстовых сообщений с кнопками меню
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🛠️ Админка"), admin_panel))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🚛 Начать смену"), start_shift))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📦 Список доставки"), delivery_list))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("💬 Чат водителей"), chat))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🅿️ Стоянка"), parking_check))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📊 Отчёт смен"), report))
    
    # Обработчики кнопок чата
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("✍️ Написать сообщение"), write_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🔄 Обновить"), refresh_chat))

    # Блокировка медиа файлов
    app.add_handler(MessageHandler(filters.PHOTO, block_media))
    app.add_handler(MessageHandler(filters.Document.ALL, block_media))
    app.add_handler(MessageHandler(filters.VIDEO, block_media))
    app.add_handler(MessageHandler(filters.AUDIO, block_media))
    app.add_handler(MessageHandler(filters.VOICE, block_media))
    app.add_handler(MessageHandler(filters.VIDEO_NOTE, block_media))
    app.add_handler(MessageHandler(filters.Sticker.ALL, block_media))

    # Запуск бота
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()