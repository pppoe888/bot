from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_role_selection():
    """Клавиатура выбора роли"""
    keyboard = [
        ["👨‍💼 Администратор"],
        ["📋 Логист"],
        ["🚛 Водитель"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_phone_request_keyboard():
    """Клавиатура для запроса номера телефона"""
    keyboard = [
        [KeyboardButton("📱 Поделиться контактом", request_contact=True)],
        ["⬅️ Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_admin_menu():
    """Клавиатура админ панели (обычная)"""
    keyboard = [
        ["👥 Управление водителями", "🚗 Управление машинами"],
        ["📋 Управление логистами", "📊 Статистика"],
        ["⬅️ Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_inline_keyboard():
    """Инлайн клавиатура админ панели"""
    keyboard = [
        [InlineKeyboardButton("👥 Управление водителями", callback_data="manage_drivers")],
        [InlineKeyboardButton("🚗 Управление машинами", callback_data="manage_cars")],
        [InlineKeyboardButton("📋 Управление логистами", callback_data="manage_logists")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_driver_menu():
    """Меню водителя"""
    keyboard = [
        ["🚛 Начать смену", "📦 Список поставок"],
        ["💬 Чат", "🅿️ Парковка"],
        ["📊 Отчет"]
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
        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manage_cars_keyboard():
    """Клавиатура управления машинами"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить машину", callback_data="add_car")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manage_logists_keyboard():
    """Клавиатура управления логистами"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить логиста", callback_data="add_logist")],
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