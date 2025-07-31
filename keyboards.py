from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def get_contact_keyboard():
    """Клавиатура для запроса контакта"""
    keyboard = [[KeyboardButton("📱 Поделиться номером", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_role_selection():
    """Клавиатура выбора роли"""
    keyboard = [
        ["👨‍💼 Администратор"],
        ["📋 Логист", "🚛 Водитель"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_phone_request_keyboard():
    """Клавиатура для запроса номера телефона"""
    keyboard = [
        [KeyboardButton("📱 Поделиться контактом", request_contact=True)],
        ["⬅️ Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)



def get_admin_inline_keyboard():
    """Inline клавиатура для админа"""
    keyboard = [
        [InlineKeyboardButton("🚗 Автомобили", callback_data="admin_cars")],
        [InlineKeyboardButton("👥 Сотрудники", callback_data="admin_employees")],
        [InlineKeyboardButton("🚛 Смены", callback_data="admin_shifts")],
        [InlineKeyboardButton("📊 Отчеты", callback_data="admin_reports")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_cars_keyboard():
    """Клавиатура раздела автомобили"""
    keyboard = [
        [InlineKeyboardButton("🚗 Управление машинами", callback_data="manage_cars")],
        [InlineKeyboardButton("📊 Статистика по машинам", callback_data="cars_stats")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_employees_keyboard():
    """Клавиатура раздела сотрудники"""
    keyboard = [
        [InlineKeyboardButton("👤 Управление водителями", callback_data="manage_drivers")],
        [InlineKeyboardButton("📋 Управление логистами", callback_data="manage_logists")],
        [InlineKeyboardButton("📊 Статистика по сотрудникам", callback_data="employees_stats")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_shifts_keyboard():
    """Клавиатура раздела смены"""
    keyboard = [
        [InlineKeyboardButton("🚛 Активные смены", callback_data="show_active_shifts")],
        [InlineKeyboardButton("📋 История смен", callback_data="shifts_history")],
        [InlineKeyboardButton("📊 Статистика смен", callback_data="shifts_stats")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_reports_keyboard():
    """Клавиатура раздела отчеты"""
    keyboard = [
        [InlineKeyboardButton("📈 Общая статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("📊 Отчет по сменам", callback_data="shifts_report")],
        [InlineKeyboardButton("🚗 Отчет по машинам", callback_data="cars_report")],
        [InlineKeyboardButton("👥 Отчет по сотрудникам", callback_data="employees_report")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_driver_menu():
    """Меню водителя"""
    keyboard = [
        ["🚛 Начать смену"],
        ["🗺️ Маршрут"],
        ["⚠️ Сообщить о проблеме"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_logist_menu():
    """Меню логиста"""
    keyboard = [
        ["📦 Список доставки"],
        ["💬 Чат водителей"],
        ["📊 Отчёт смен"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard():
    """Клавиатура с кнопкой назад"""
    keyboard = [["⬅️ Назад"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_chat_menu():
    """Клавиатура для чата"""
    keyboard = [
        ["✍️ Написать сообщение", "🔄 Обновить"],
        ["⬅️ Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_chat_keyboard():
    """Клавиатура для чата"""
    keyboard = [
        ["✍️ Написать сообщение", "🔄 Обновить"],
        ["⬅️ Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_confirm_keyboard():
    """Клавиатура подтверждения"""
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm")],
        [InlineKeyboardButton("❌ Отменить", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manage_drivers_keyboard():
    """Клавиатура управления водителями"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить водителя", callback_data="add_driver")],
        [InlineKeyboardButton("📝 Редактировать водителя", callback_data="edit_driver_list")],
        [InlineKeyboardButton("🗑️ Удалить водителя", callback_data="delete_driver_list")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manage_logists_keyboard():
    """Клавиатура управления логистами"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить логиста", callback_data="add_logist")],
        [InlineKeyboardButton("📝 Редактировать логиста", callback_data="edit_logist_list")],
        [InlineKeyboardButton("🗑️ Удалить логиста", callback_data="delete_logist_list")],
        [InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_user_list_keyboard(users, action_type):
    """Клавиатура со списком пользователей для действий"""
    keyboard = []
    for user in users:
        callback_data = f"{action_type}_{user.id}"
        keyboard.append([InlineKeyboardButton(f"{user.name} ({user.phone})", callback_data=callback_data)])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_panel")])
    return InlineKeyboardMarkup(keyboard)

def get_edit_user_keyboard(user_id, user_type):
    """Клавиатура для редактирования пользователя"""
    keyboard = [
        [InlineKeyboardButton("📝 Изменить имя", callback_data=f"edit_name_{user_type}_{user_id}")],
        [InlineKeyboardButton("📱 Изменить телефон", callback_data=f"edit_phone_{user_type}_{user_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"manage_{user_type}s")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manage_cars_keyboard():
    """Клавиатура управления машинами"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить машину", callback_data="add_car")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_car_selection_keyboard(cars):
    """Клавиатура выбора машины"""
    keyboard = []
    for car in cars:
        keyboard.append([InlineKeyboardButton(
            f"🚗 {car.number} ({car.brand} {car.model})",
            callback_data=f"select_car_{car.id}"
        )])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel")])
    return InlineKeyboardMarkup(keyboard)