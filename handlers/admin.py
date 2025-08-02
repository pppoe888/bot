from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import SessionLocal, User, Car, Shift, CargoItem, ShiftPhoto
from keyboards import get_admin_inline_keyboard, get_manage_drivers_keyboard, get_manage_logists_keyboard, get_manage_cars_keyboard
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

async def find_user_by_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Поиск пользователя по имени для диагностики"""
    query = update.callback_query
    await query.answer()
    
    text = "🔍 ДИАГНОСТИКА ПОЛЬЗОВАТЕЛЯ\n\n"
    text += "Введите имя пользователя для поиска:"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    except:
        message = await query.message.reply_text(text=text, reply_markup=reply_markup)
        context.user_data["last_message_id"] = message.message_id
    
    context.user_data["awaiting_user_search"] = True

async def search_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE, search_name: str):
    """Поиск информации о пользователе"""
    db = SessionLocal()
    try:
        # Ищем пользователей по имени (частичное совпадение)
        users = db.query(User).filter(User.name.like(f"%{search_name}%")).all()
        
        if not users:
            text = f"❌ Пользователь с именем '{search_name}' не найден в базе данных.\n\n"
            text += "Возможные причины:\n"
            text += "• Пользователь не был добавлен администратором\n"
            text += "• Неточное написание имени\n"
            text += "• Пользователь был удален\n\n"
            text += "Рекомендации:\n"
            text += "1. Проверьте правильность написания имени\n"
            text += "2. Добавьте пользователя через админ панель\n"
            text += "3. Проверьте список всех пользователей"
        else:
            text = f"✅ Найдено пользователей: {len(users)}\n\n"
            
            for i, user in enumerate(users, 1):
                text += f"👤 Пользователь {i}:\n"
                text += f"• Имя: {user.name}\n"
                text += f"• Телефон: {user.phone}\n"
                text += f"• Роль: {user.role}\n"
                text += f"• Telegram ID: {user.telegram_id or 'Не привязан'}\n"
                
                if not user.telegram_id:
                    text += "⚠️ ПРОБЛЕМА: Telegram ID не привязан\n"
                
                text += "\n"
            
            if any(not user.telegram_id for user in users):
                text += "🔧 РЕШЕНИЕ ПРОБЛЕМ:\n"
                text += "• Пользователь должен отправить свой контакт боту\n"
                text += "• Проверьте правильность номера телефона\n"
                text += "• Убедитесь что пользователь выбрал правильную роль\n"
        
        keyboard = [
            [InlineKeyboardButton("🔍 Найти другого", callback_data="find_user_by_name")],
            [InlineKeyboardButton("👥 Все пользователи", callback_data="employees_list")],
            [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
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
            text=text,
            reply_markup=reply_markup
        )
        context.user_data["last_message_id"] = message.message_id
        context.user_data.pop("awaiting_user_search", None)
        
    finally:
        db.close()

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ панель"""
    text = "Администрирование"

    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
    except:
        message = await update.callback_query.message.reply_text(
            text=text,
            reply_markup=get_admin_inline_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    await update.callback_query.answer()



# === НОВЫЕ РАЗДЕЛЫ АДМИНКИ ===

async def admin_cars_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Раздел автомобили"""
    from keyboards import get_admin_cars_keyboard

    text = "Автомобили"

    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_admin_cars_keyboard()
        )
    except:
        message = await update.callback_query.message.reply_text(
            text=text,
            reply_markup=get_admin_cars_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    await update.callback_query.answer()

async def admin_employees_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Раздел сотрудники"""
    from keyboards import get_admin_employees_keyboard

    text = "Сотрудники"

    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_admin_employees_keyboard()
        )
    except:
        message = await update.callback_query.message.reply_text(
            text=text,
            reply_markup=get_admin_employees_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    await update.callback_query.answer()

async def admin_shifts_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Раздел смены"""
    from keyboards import get_admin_shifts_keyboard

    text = "Раздел: Смены\n\nВыберите действие:"

    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_admin_shifts_keyboard()
        )
    except:
        message = await update.callback_query.message.reply_text(
            text=text,
            reply_markup=get_admin_shifts_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    await update.callback_query.answer()

async def admin_reports_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Раздел отчеты"""
    from keyboards import get_admin_reports_keyboard

    text = "Раздел: Отчеты\n\nВыберите тип отчета:"

    try:
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=get_admin_reports_keyboard()
        )
    except:
        message = await update.callback_query.message.reply_text(
            text=text,
            reply_markup=get_admin_reports_keyboard()
        )
        context.user_data["last_message_id"] = message.message_id

    await update.callback_query.answer()



async def employees_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика по сотрудникам"""
    from keyboards import get_admin_employees_keyboard

    db = SessionLocal()
    try:
        drivers_count = db.query(User).filter(User.role == "driver").count()
        logists_count = db.query(User).filter(User.role == "logist").count()
        active_drivers = db.query(Shift).filter(Shift.is_active == True).count()

        text = "Статистика по сотрудникам\n\n"
        text += f"Всего водителей: {drivers_count}\n"
        text += f"На смене: {active_drivers}\n"
        text += f"Логистов: {logists_count}"

        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=get_admin_employees_keyboard()
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=get_admin_employees_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await update.callback_query.answer()

async def shifts_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика по сменам"""
    from keyboards import get_admin_shifts_keyboard

    db = SessionLocal()
    try:
        active_shifts = db.query(Shift).filter(Shift.is_active == True).count()
        total_shifts = db.query(Shift).count()
        completed_shifts = total_shifts - active_shifts

        text = "Статистика по сменам\n\n"
        text += f"Активных смен: {active_shifts}\n"
        text += f"Завершенных смен: {completed_shifts}\n"
        text += f"Всего смен: {total_shifts}"

        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=get_admin_shifts_keyboard()
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=get_admin_shifts_keyboard()
            )
            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await update.callback_query.answer()

async def view_car_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр информации об автомобиле смены"""
    from keyboards import get_back_to_shift_keyboard

    query = update.callback_query
    shift_id = int(query.data.split("_")[3])

    db = SessionLocal()
    try:
        shift = db.query(Shift).filter(Shift.id == shift_id).first()

        if not shift:
            await query.answer("Смена не найдена!")
            return

        car = shift.car
        text = f"🚗 ИНФОРМАЦИЯ ОБ АВТОМОБИЛЕ\n\n"
        text += f"📋 Номер: {car.number}\n"
        text += f"🏭 Марка: {car.brand or 'Не указана'}\n"
        text += f"🚙 Модель: {car.model or 'Не указана'}\n"
        text += f"⛽ Топливо: {car.fuel or 'Не указано'}\n"
        text += f"🛣️ Пробег: {car.current_mileage} км\n"
        text += f"📅 Добавлен: {car.created_at.strftime('%d.%m.%Y')}"

        try:
            await query.edit_message_text(
                text=text,
                reply_markup=get_back_to_shift_keyboard(shift_id)
            )
        except:
            message = await query.message.reply_text(
                text=text,
                reply_markup=get_back_to_shift_keyboard(shift_id)
            )
            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await query.answer()

async def view_delivered_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр доставленных товаров"""
    from keyboards import get_back_to_shift_keyboard

    query = update.callback_query
    shift_id = int(query.data.split("_")[2])

    db = SessionLocal()
    try:
        # Пока что показываем все загруженные товары как доставленные
        # В будущем можно добавить отдельное поле для доставки
        cargo_items = db.query(CargoItem).filter(
            CargoItem.shift_id == shift_id,
            CargoItem.is_loaded == True
        ).all()

        if not cargo_items:
            text = "🚚 Доставленные товары не найдены"
        else:
            text = f"🚚 ДОСТАВЛЕННЫЕ ТОВАРЫ (Смена #{shift_id})\n\n"

            for item in cargo_items:
                text += f"✅ {item.item_number} - {item.item_name}\n"
                if item.loaded_at:
                    text += f"   📦 Загружен: {item.loaded_at.strftime('%d.%m.%Y %H:%M')}\n"
                text += "\n"

        try:
            await query.edit_message_text(
                text=text,
                reply_markup=get_back_to_shift_keyboard(shift_id)
            )
        except:
            message = await query.message.reply_text(
                text=text,
                reply_markup=get_back_to_shift_keyboard(shift_id)
            )
            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await query.answer()

async def view_shift_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр деталей смены"""
    query = update.callback_query
    shift_id = int(query.data.split("_")[2])

    db = SessionLocal()
    try:
        shift = db.query(Shift).filter(Shift.id == shift_id).first()

        if not shift:
            await query.answer("Смена не найдена!")
            return

        driver = shift.driver
        car = shift.car

        status = "🟢 Активна" if shift.is_active else "🔴 Завершена"

        text = f"📋 ДЕТАЛИ СМЕНЫ #{shift.id}\n\n"
        text += f"👤 Водитель: {driver.name}\n"
        text += f"📱 Телефон: {driver.phone}\n"
        text += f"🚗 Автомобиль: {car.number}"
        if car.brand:
            text += f" ({car.brand}"
            if car.model:
                text += f" {car.model}"
            text += ")"
        text += f"\n📊 Статус: {status}\n"
        text += f"⏰ Начало: {shift.start_time.strftime('%d.%m.%Y %H:%M')}\n"

        if shift.end_time:
            text += f"⏰ Окончание: {shift.end_time.strftime('%d.%m.%Y %H:%M')}\n"
            duration = shift.end_time - shift.start_time
            text += f"⏱️ Продолжительность: {duration.total_seconds() / 3600:.1f} ч"

        from keyboards import get_shift_details_keyboard
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=get_shift_details_keyboard(shift_id)
            )
        except:
            message = await query.message.reply_text(
                text=text,
                reply_markup=get_shift_details_keyboard(shift_id)
            )
            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await query.answer()

async def view_shift_photos_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр информации о фотографиях в БД"""
    query = update.callback_query
    shift_id = int(query.data.split("_")[3])

    db = SessionLocal()
    try:
        shift = db.query(Shift).filter(Shift.id == shift_id).first()
        if not shift:
            await query.answer("Смена не найдена!")
            return

        # Получаем фото из базы данных
        photos = db.query(ShiftPhoto).filter(ShiftPhoto.shift_id == shift_id).order_by(ShiftPhoto.created_at).all()

        text = f"📋 ИНФОРМАЦИЯ О ФОТО В БАЗЕ ДАННЫХ\n\n"
        text += f"👤 Водитель: {shift.driver.name}\n"
        text += f"🚗 Автомобиль: {shift.car.number}\n"
        text += f"📅 Смена: {shift.start_time.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"📊 Статус смены: {'🟢 Активна' if shift.is_active else '🔴 Завершена'}\n\n"

        if not photos:
            text += "❌ Фотографии в базе данных отсутствуют\n"
            text += "Возможные причины:\n"
            text += "• Осмотр не проводился\n"
            text += "• Ошибка сохранения фото\n"
            text += "• Данные были удалены"
        else:
            text += f"📸 ФОТОГРАФИИ В БД: {len(photos)} шт.\n\n"
            
            photo_names = {
                'front': '🚗 Передняя часть',
                'back': '🚙 Задняя часть',
                'left': '⬅️ Левый борт',
                'right': '➡️ Правый борт', 
                'oil': '🛢️ Уровень масла',
                'coolant': '❄️ Охлаждающая жидкость',
                'interior': '🪑 Салон автомобиля'
            }
            
            for i, photo in enumerate(photos, 1):
                photo_name = photo_names.get(photo.photo_type, f"Неизвестный тип: {photo.photo_type}")
                text += f"{i}. {photo_name}\n"
                text += f"   🆔 БД ID: {photo.id}\n"
                text += f"   📄 Telegram File ID: ...{photo.file_id[-15:]}\n"
                text += f"   📅 Сохранено: {photo.created_at.strftime('%d.%m.%Y %H:%M:%S')}\n\n"

        # Кнопки
        buttons = []
        if photos:
            buttons.append([InlineKeyboardButton("📸 Показать все фото", callback_data=f"view_photos_{shift_id}")])
        buttons.append([InlineKeyboardButton("🔙 Назад к смене", callback_data=f"view_shift_{shift_id}")])

        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    finally:
        db.close()

    await query.answer()

async def view_shift_inspection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр фотографий осмотра смены"""
    query = update.callback_query
    shift_id = int(query.data.split("_")[2])

    db = SessionLocal()
    try:
        shift = db.query(Shift).filter(Shift.id == shift_id).first()
        if not shift:
            await query.answer("Смена не найдена!")
            return

        # Получаем фото из базы данных
        photos = db.query(ShiftPhoto).filter(ShiftPhoto.shift_id == shift_id).order_by(ShiftPhoto.created_at).all()

        if not photos:
            text = f"📸 ФОТО ОСМОТРА\n\n"
            text += f"👤 Водитель: {shift.driver.name}\n"
            text += f"🚗 Автомобиль: {shift.car.number}\n\n"
            text += "❌ Фотографии осмотра не найдены в базе данных"

            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад к смене", callback_data=f"view_shift_{shift_id}")
                ]])
            )
        else:
            # Названия типов фото
            photo_names = {
                'front': '🚗 Передняя часть',
                'back': '🚙 Задняя часть',
                'left': '⬅️ Левый борт', 
                'right': '➡️ Правый борт',
                'oil': '🛢️ Уровень масла',
                'coolant': '❄️ Охлаждающая жидкость',
                'interior': '🪑 Салон автомобиля'
            }

            # Отправляем заголовок
            header_text = f"📸 ФОТО ОСМОТРА АВТОМОБИЛЯ\n\n"
            header_text += f"👤 Водитель: {shift.driver.name}\n"
            header_text += f"🚗 Автомобиль: {shift.car.number}\n"
            header_text += f"📅 Дата смены: {shift.start_time.strftime('%d.%m.%Y %H:%M')}\n"
            header_text += f"📸 Количество фото: {len(photos)} шт.\n\n"
            header_text += "Загружаю фотографии из базы данных..."

            await query.edit_message_text(
                text=header_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад к смене", callback_data=f"view_shift_{shift_id}")
                ]])
            )

            # Отправляем каждое фото
            for i, photo in enumerate(photos, 1):
                photo_name = photo_names.get(photo.photo_type, f"Фото {photo.photo_type}")
                
                try:
                    caption = f"📸 {photo_name}\n"
                    caption += f"👤 {shift.driver.name} | 🚗 {shift.car.number}\n"
                    caption += f"📊 Фото {i} из {len(photos)}\n"
                    caption += f"🆔 БД ID: {photo.id} | File ID: ...{photo.file_id[-10:]}\n"
                    caption += f"📅 {photo.created_at.strftime('%d.%m.%Y %H:%M')}"

                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo.file_id,
                        caption=caption
                    )
                except Exception as e:
                    print(f"Ошибка отправки фото ID {photo.id}: {e}")
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"❌ Ошибка загрузки фото: {photo_name}\n🆔 БД ID: {photo.id}\n📄 File ID: {photo.file_id}\n⚠️ Ошибка: {str(e)}"
                    )

            # Финальное сообщение
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Показаны все фотографии осмотра из базы данных!\n\n📋 Смена #{shift_id}\n👤 {shift.driver.name}\n🚗 {shift.car.number}\n📸 Фото: {len(photos)} шт.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад к смене", callback_data=f"view_shift_{shift_id}")
                ]])
            )

    finally:
        db.close()

    await query.answer()

async def view_shift_cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр загруженных товаров смены"""
    from keyboards import get_back_to_shift_keyboard

    query = update.callback_query
    shift_id = int(query.data.split("_")[2])

    db = SessionLocal()
    try:
        cargo_items = db.query(CargoItem).filter(
            CargoItem.shift_id == shift_id,
            CargoItem.is_loaded == True
        ).all()

        if not cargo_items:
            text = "📦 Загруженные товары не найдены"
        else:
            text = f"📦 ЗАГРУЖЕННЫЕ ТОВАРЫ (Смена #{shift_id})\n\n"

            for item in cargo_items:
                text += f"✅ {item.item_number} - {item.item_name}\n"
                if item.loaded_at:
                    text += f"   📅 Загружен: {item.loaded_at.strftime('%d.%m.%Y %H:%M')}\n"
                text += "\n"

        try:
            await query.edit_message_text(
                text=text,
                reply_markup=get_back_to_shift_keyboard(shift_id)
            )
        except:
            message = await query.message.reply_text(
                text=text,
                reply_markup=get_back_to_shift_keyboard(shift_id)
            )
            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await query.answer()

async def active_shifts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр активных смен"""
    from keyboards import get_admin_shifts_keyboard

    db = SessionLocal()
    try:
        active_shifts_list = db.query(Shift).filter(Shift.is_active == True).all()

        if not active_shifts_list:
            text = "📋 Активных смен нет"
            keyboard = get_admin_shifts_keyboard()
        else:
            text = "🚛 АКТИВНЫЕ СМЕНЫ:\n\n"

            for shift in active_shifts_list:
                driver = shift.driver
                car = shift.car

                car_info = f"{car.number}"
                if car.brand:
                    car_info += f" ({car.brand}"
                    if car.model:
                        car_info += f" {car.model}"
                    car_info += ")"

                text += f"👤 {driver.name}\n"
                text += f"🚗 {car_info}\n"
                text += f"⏰ Начало: {shift.start_time.strftime('%H:%M')}\n"

                # Получаем загруженные товары
                loaded_items = db.query(CargoItem).filter(
                    CargoItem.shift_id == shift.id,
                    CargoItem.is_loaded == True
                ).all()

                if loaded_items:
                    text += f"📦 Загружено ({len(loaded_items)} шт.):\n"
                    for item in loaded_items:
                        text += f"   ✅ {item.item_number} - {item.item_name}\n"
                else:
                    text += "📦 Товары не загружены\n"

                # Проверяем наличие фото осмотра
                photos_count = db.query(ShiftPhoto).filter(ShiftPhoto.shift_id == shift.id).count()
                if photos_count > 0:
                    text += f"📸 Фото осмотра: {photos_count} шт.\n"
                else:
                    text += "📸 Фото осмотра: нет\n"

                text += "───────────────\n"

            # Создаем клавиатуру с кнопками для каждой активной смены
            keyboard = []
            for shift in active_shifts_list:
                driver_name = shift.driver.name

                # Добавляем только кнопку для просмотра загрузки
                keyboard.append([
                    InlineKeyboardButton(f"📦 Загрузка - {driver_name}", callback_data=f"view_cargo_{shift.id}")
                ])

            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_shifts_section")])
            keyboard = InlineKeyboardMarkup(keyboard)

        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=keyboard
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=keyboard
            )
            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await update.callback_query.answer()

async def show_active_shift_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать фотографии осмотра активной смены"""
    query = update.callback_query
    shift_id = int(query.data.split("_")[2])

    db = SessionLocal()
    try:
        shift = db.query(Shift).filter(Shift.id == shift_id).first()
        
        if not shift:
            await query.answer("Смена не найдена!")
            return

        photos = db.query(ShiftPhoto).filter(ShiftPhoto.shift_id == shift_id).all()

        if not photos:
            text = f"📸 ФОТО ОСМОТРА\n\n"
            text += f"👤 Водитель: {shift.driver.name}\n"
            text += f"🚗 Автомобиль: {shift.car.number}\n\n"
            text += "❌ Фотографии осмотра не найдены"

            try:
                await query.edit_message_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 К активным сменам", callback_data="active_shifts")
                    ]])
                )
            except:
                message = await query.message.reply_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 К активным сменам", callback_data="active_shifts")
                    ]])
                )
                context.user_data["last_message_id"] = message.message_id
        else:
            # Отвечаем на callback
            await query.answer("Отправляю фотографии...")

            # Определяем названия типов фото
            photo_names = {
                'front': '🚗 Передняя часть',
                'back': '🚙 Задняя часть',
                'left': '⬅️ Левый борт',
                'right': '➡️ Правый борт',
                'oil': '🛢️ Уровень масла',
                'coolant': '❄️ Охлаждающая жидкость',
                'interior': '🪑 Салон автомобиля'
            }

            # Изменяем существующее сообщение на заголовок
            header_text = f"📸 ФОТО ОСМОТРА\n\n"
            header_text += f"👤 Водитель: {shift.driver.name}\n"
            header_text += f"🚗 Автомобиль: {shift.car.number}\n"
            header_text += f"📅 Время начала: {shift.start_time.strftime('%d.%m.%Y %H:%M')}\n"
            header_text += f"📸 Отправляю {len(photos)} фотографий..."

            try:
                await query.edit_message_text(
                    text=header_text,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 К активным сменам", callback_data="active_shifts")
                    ]])
                )
            except:
                pass

            # Отправляем каждое фото отдельно с подписью
            for i, photo in enumerate(photos, 1):
                photo_name = photo_names.get(photo.photo_type, f"Фото {photo.photo_type}")
                
                try:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo.file_id,
                        caption=f"📸 {photo_name}\n👤 {shift.driver.name} | 🚗 {shift.car.number}\n📊 Фото {i} из {len(photos)}"
                    )
                except Exception as e:
                    print(f"Ошибка отправки фото {photo.id}: {e}")
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"❌ Ошибка загрузки фото: {photo_name}\nFile ID: {photo.file_id}"
                    )

            # Отправляем итоговое сообщение с кнопкой "Назад"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Все фотографии отправлены!\n\n👤 Водитель: {shift.driver.name}\n🚗 Автомобиль: {shift.car.number}\n📸 Всего фото: {len(photos)}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К активным сменам", callback_data="active_shifts")
                ]])
            )

    except Exception as e:
        print(f"Ошибка в show_active_shift_photos: {e}")
        try:
            await query.answer("Ошибка при загрузке фотографий!")
            await query.edit_message_text(
                text=f"❌ Ошибка при загрузке фотографий: {str(e)}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К активным сменам", callback_data="active_shifts")
                ]])
            )
        except:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Ошибка при загрузке фотографий: {str(e)}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К активным сменам", callback_data="active_shifts")
                ]])
            )
    finally:
        db.close()

async def view_history_shift_inspection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр фотографий осмотра из истории смен"""
    query = update.callback_query
    shift_id = int(query.data.split("_")[3])

    db = SessionLocal()
    try:
        shift = db.query(Shift).filter(Shift.id == shift_id).first()
        photos = db.query(ShiftPhoto).filter(ShiftPhoto.shift_id == shift_id).all()

        if not shift:
            await query.answer("Смена не найдена!")
            return

        if not photos:
            text = f"📸 ФОТО ОСМОТРА\n\n"
            text += f"👤 Водитель: {shift.driver.name}\n"
            text += f"🚗 Автомобиль: {shift.car.number}\n\n"
            text += "❌ Фотографии осмотра не найдены"

            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К истории смен", callback_data="shifts_history")
                ]])
            )
        else:
            # Отправляем заголовок
            text = f"📸 ФОТО ОСМОТРА\n\n"
            text += f"👤 Водитель: {shift.driver.name}\n"
            text += f"🚗 Автомобиль: {shift.car.number}\n"
            text += f"📅 Время начала: {shift.start_time.strftime('%d.%m.%Y %H:%M')}\n\n"
            text += f"📸 Отправляю {len(photos)} фотографий в чат..."

            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К активным сменам", callback_data="active_shifts")
                ]])
            )

            # Отправляем каждое фото в чат
            photo_names = {
                'front': '🚗 Передняя часть',
                'back': '🚙 Задняя часть', 
                'left': '⬅️ Левый борт',
                'right': '➡️ Правый борт',
                'oil': '🛢️ Уровень масла',
                'coolant': '❄️ Охлаждающая жидкость',
                'interior': '🪑 Салон автомобиля'
            }

            for i, photo in enumerate(photos, 1):
                photo_name = photo_names.get(photo.photo_type, photo.photo_type)
                try:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo.file_id,
                        caption=f"📸 {photo_name}\n👤 {shift.driver.name} | 🚗 {shift.car.number}\n📊 Фото {i} из {len(photos)}"
                    )
                except Exception as e:
                    print(f"Ошибка отправки фото: {e}")
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"❌ Ошибка загрузки фото: {photo_name}"
                    )

            # Отправляем итоговое сообщение
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Все фотографии осмотра отправлены!\n\n👤 Водитель: {shift.driver.name}\n🚗 Автомобиль: {shift.car.number}\n📸 Всего фото: {len(photos)}"
            )

    finally:
        db.close()

    await query.answer()



async def view_active_shift_cargo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Просмотр загруженных товаров активной смены"""
    query = update.callback_query
    shift_id = int(query.data.split("_")[2])

    db = SessionLocal()
    try:
        shift = db.query(Shift).filter(Shift.id == shift_id).first()

        if not shift:
            await query.answer("Смена не найдена!")
            return

        # Получаем все товары для загрузки (загруженные и незагруженные)
        all_items = db.query(CargoItem).filter(CargoItem.shift_id == shift_id).all()
        loaded_items = [item for item in all_items if item.is_loaded]
        pending_items = [item for item in all_items if not item.is_loaded]

        text = f"📦 СОСТОЯНИЕ ЗАГРУЗКИ\n\n"
        text += f"👤 Водитель: {shift.driver.name}\n"
        text += f"🚗 Автомобиль: {shift.car.number}\n"
        text += f"📅 Время начала: {shift.start_time.strftime('%d.%m.%Y %H:%M')}\n\n"

        if loaded_items:
            text += f"✅ ЗАГРУЖЕНО ({len(loaded_items)} шт.):\n"
            for item in loaded_items:
                load_time = item.loaded_at.strftime('%H:%M') if item.loaded_at else 'неизвестно'
                text += f"   • {item.item_number} - {item.item_name}\n"
                text += f"     ⏰ Загружен в {load_time}\n"
            text += "\n"

        if pending_items:
            text += f"⏳ ОЖИДАЕТ ЗАГРУЗКИ ({len(pending_items)} шт.):\n"
            for item in pending_items:
                text += f"   • {item.item_number} - {item.item_name}\n"
            text += "\n"

        if not all_items:
            text += "❌ Товары для загрузки не назначены"

        text += f"\n📊 Прогресс: {len(loaded_items)}/{len(all_items)} товаров загружено"

        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К активным сменам", callback_data="active_shifts")
            ]])
        )
    finally:
        db.close()

    await query.answer()

async def shifts_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """История смен"""
    from keyboards import get_shifts_history_keyboard

    db = SessionLocal()
    try:
        shifts = db.query(Shift).order_by(Shift.start_time.desc()).limit(20).all()

        if not shifts:
            text = "📋 История смен пуста"
            keyboard = get_admin_shifts_keyboard()
        else:
            text = "📋 ИСТОРИЯ СМЕН\n\nПоследние 20 смен (нажмите для подробностей):"
            keyboard = get_shifts_history_keyboard(shifts)

        try:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=keyboard
            )
        except:
            message = await update.callback_query.message.reply_text(
                text=text,
                reply_markup=keyboard
            )
            context.user_data["last_message_id"] = message.message_id
    finally:
        db.close()

    await update.callback_query.answer()