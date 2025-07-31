from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

def get_phone_button():
    """Клавиатура для отправки номера телефона"""
    keyboard = [[KeyboardButton("📱 Отправить номер", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_driver_menu():
    """Главное меню водителя"""
    keyboard = [
        ["🚛 Начать смену", "📦 Список доставки"],
        ["💬 Чат водителей", "🅿️ Стоянка"],
        ["📊 Отчёт смен"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def get_admin_menu():
    """Главное меню администратора"""
    keyboard = [
        ["🛠️ Админка", "🚛 Начать смену"],
        ["📦 Список доставки", "💬 Чат водителей"],
        ["🅿️ Стоянка", "📊 Отчёт смен"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

def get_admin_inline_keyboard():
    """Inline клавиатура для админ панели"""
    keyboard = [
        [InlineKeyboardButton("👥 Управление водителями", callback_data="manage_drivers")],
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