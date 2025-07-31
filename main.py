from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
from handlers.auth import start, handle_contact, create_admin, handle_role_selection
from handlers.driver import start_shift
from handlers.delivery import delivery_list
from handlers.admin import admin_panel, manage_drivers, manage_cars, manage_logists
from handlers.admin_actions import handle_admin_text, handle_add_driver, handle_add_logist, handle_add_car
from handlers.chat import chat, write_message, send_message_to_chat, refresh_chat
from handlers.parking import parking_check
from handlers.report import report
from states import WAITING_ROLE_SELECTION
from database import SessionLocal, User, Car

async def delete_previous_messages(update, context):
    """Удаляет предыдущие сообщения для очистки чата"""
    try:
        if context.user_data.get("last_message_id"):
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=context.user_data["last_message_id"]
            )

        if update.message:
            await update.message.delete()

        message_ids_to_delete = context.user_data.get("message_history", [])
        for msg_id in message_ids_to_delete[-5:]:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=msg_id
                )
            except:
                continue

        context.user_data["message_history"] = []

    except Exception as e:
        pass

async def save_message_to_history(context, message_id):
    """Сохраняет ID сообщения в историю для последующего удаления"""
    if "message_history" not in context.user_data:
        context.user_data["message_history"] = []

    context.user_data["message_history"].append(message_id)

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
    from keyboards import get_admin_menu, get_driver_menu, get_logist_menu, get_role_selection
    from database import SessionLocal, User

    await delete_previous_messages(update, context)

    # Очищаем состояния
    context.user_data.pop("state", None)
    context.user_data.pop("admin_action", None)
    context.user_data.pop("driver_data", None)
    context.user_data.pop("logist_data", None)
    context.user_data.pop("car_data", None)

    # Определяем роль пользователя и показываем соответствующее меню
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

        if user:
            if user.role == "admin":
                keyboard = get_admin_menu()
                text = f"Добро пожаловать, Администратор {user.name}!"
            elif user.role == "driver":
                keyboard = get_driver_menu()
                text = f"Добро пожаловать, водитель {user.name}!"
            elif user.role == "logist":
                keyboard = get_logist_menu()
                text = f"Добро пожаловать, логист {user.name}!"
            else:
                keyboard = get_role_selection()
                text = "Выберите вашу роль:"
                context.user_data["state"] = WAITING_ROLE_SELECTION
        else:
            keyboard = get_role_selection()
            text = "Выберите вашу роль:"
            context.user_data["state"] = WAITING_ROLE_SELECTION

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=keyboard
        )
        context.user_data["last_message_id"] = message.message_id

    finally:
        db.close()

async def confirm_add_driver(update, context):
    """Подтверждение добавления водителя"""
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
            telegram_id=0,
            name=driver_data["name"],
            phone=driver_data["phone"],
            role="driver"
        )
        db.add(new_driver)
        db.commit()

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

async def confirm_add_logist(update, context):
    """Подтверждение добавления логиста"""
    from keyboards import get_admin_menu

    logist_data = context.user_data.get("logist_data", {})

    if not logist_data.get("name") or not logist_data.get("phone"):
        await delete_previous_messages(update, context)
        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Не все данные введены"
        )
        context.user_data["last_message_id"] = message.message_id
        return

    db = SessionLocal()
    try:
        new_logist = User(
            telegram_id=0,
            name=logist_data["name"],
            phone=logist_data["phone"],
            role="logist"
        )
        db.add(new_logist)
        db.commit()

        await delete_previous_messages(update, context)

        message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Логист {logist_data['name']} успешно добавлен!",
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

async def handle_confirm(update, context):
    """Универсальный обработчик подтверждения"""
    admin_action = context.user_data.get("admin_action")
    
    if admin_action == "adding_driver":
        await confirm_add_driver(update, context)
    elif admin_action == "adding_logist":
        await confirm_add_logist(update, context)
    elif admin_action == "adding_car":
        await confirm_add_car(update, context)

async def confirm_add_car(update, context):
    """Подтверждение добавления машины"""
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
    app.add_handler(CallbackQueryHandler(lambda u, c: manage_logists(u, c), pattern="^manage_logists$"))
    app.add_handler(CallbackQueryHandler(handle_add_driver, pattern="^add_driver$"))
    app.add_handler(CallbackQueryHandler(handle_add_logist, pattern="^add_logist$"))
    app.add_handler(CallbackQueryHandler(handle_add_car, pattern="^add_car$"))

    # Обработчики подтверждения
    app.add_handler(CallbackQueryHandler(handle_confirm, pattern="^confirm$"))

    # Обработчик для выбора роли
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex("^(👨‍💼 Администратор|📋 Логист|🚛 Водитель)$"), 
        handle_role_selection
    ))

    # Обработчик для админских действий
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🛠️|🚛|📦|💬|🅿️|📊|⬅️|✅|❌|✍️|🔄|👨‍💼|📋)") & ~filters.Regex("^(Водитель|Логист|Администратор)"), 
        handle_admin_text
    ))

    # Обработчики текстовых сообщений с кнопками меню
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🛠️ Админка"), admin_panel))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🚛 Начать смену"), start_shift))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📦 Заказы"), delivery_list))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("💬 Чат"), chat))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🅿️ Стоянка"), parking_check))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📊 Отчет"), report))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("⬅️ Назад"), handle_back_button))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("✍️ Написать сообщение"), write_message))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("🔄 Обновить"), refresh_chat))

    # Обработчик сообщений для чата
    app.add_handler(MessageHandler(filters.TEXT, send_message_to_chat))

    # Блокировка медиа
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.DOCUMENT | filters.AUDIO, block_media))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()