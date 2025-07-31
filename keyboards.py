from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

def get_role_selection():
    """Клавиатура выбора роли"""
    keyboard = [
        ["👨‍💼 Администратор"],
        ["📋 Логист", "🚛 Водитель"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_phone_button():
    """Клавиатура для отправки номера телефона"""
    keyboard = [
        [KeyboardButton("📱 Отправить номер телефона", request_contact=True)],
        ["⬅️ Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_admin_menu():
    """Главное меню администратора"""
    keyboard = [
        ["🛠️ Админка", "🚛 Начать смену"],
        ["📦 Список доставки", "💬 Чат водителей"],
        ["🅿️ Стоянка", "📊 Отчёт смен"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def get_driver_menu():
    """Меню водителя"""
    keyboard = [
        ["🚛 Начать смену"],
        ["📦 Список доставки"],
        ["💬 Чат водителей"],
        ["🅿️ Стоянка", "📊 Отчёт смен"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_logist_menu():
    """Меню логиста"""
    keyboard = [
        ["📦 Список доставки"],
        ["💬 Чат водителей"],
        ["📊 Отчёт смен", "🅿️ Стоянка"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_inline_keyboard():
    """Inline клавиатура для админ панели"""
    keyboard = [
        [InlineKeyboardButton("👥 Управление водителями", callback_data="manage_drivers")],
        [InlineKeyboardButton("📋 Управление логистами", callback_data="manage_logists")],
        [InlineKeyboardButton("🚗 Управление машинами", callback_data="manage_cars")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_car_keyboard(cars):
    """Клавиатура для выбора машины"""
    keyboard = []
    for car in cars:
        keyboard.append([InlineKeyboardButton(f"🚗 {car.number}", callback_data=f"select_car_{car.id}")])
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard():
    """Клавиатура подтверждения"""
    keyboard = [
        ["✅ Подтвердить", "❌ Отменить"],
        ["⬅️ Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def get_back_keyboard():
    """Клавиатура с кнопкой назад"""
    keyboard = [["⬅️ Назад"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_chat_keyboard(mode="normal"):
    """Клавиатура для чата"""
    if mode == "cancel":
        keyboard = [["❌ Отменить"]]
    else:
        keyboard = [
            ["✍️ Написать сообщение", "🔄 Обновить"],
            ["⬅️ Назад"]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_manage_drivers_keyboard():
    """Клавиатура управления водителями"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить водителя", callback_data="add_driver")],
        [InlineKeyboardButton("📋 Список водителей", callback_data="list_drivers")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manage_cars_keyboard():
    """Клавиатура управления машинами"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить машину", callback_data="add_car")],
        [InlineKeyboardButton("📋 Список машин", callback_data="list_cars")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manage_logists_keyboard():
    """Клавиатура управления логистами"""
    keyboard = [
        [InlineKeyboardButton("➕ Добавить логиста", callback_data="add_logist")],
        [InlineKeyboardButton("📋 Список логистов", callback_data="list_logists")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_keyboard():
    """Inline клавиатура подтверждения"""
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_chat_menu():
    """Клавиатура меню чата"""
    keyboard = [
        ["✍️ Написать сообщение", "🔄 Обновить"],
        ["⬅️ Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)