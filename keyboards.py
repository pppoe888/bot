from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def get_start_keyboard():
    """Стартовая клавиатура"""
    keyboard = [
        [InlineKeyboardButton("Отправить контакт", request_contact=True)]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_role_selection():
    """Клавиатура выбора роли"""
    keyboard = [
        [InlineKeyboardButton("Водитель", callback_data="role_driver")],
        [InlineKeyboardButton("Логист", callback_data="role_logist")],
        [InlineKeyboardButton("Администратор", callback_data="role_admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_role_keyboard():
    """Клавиатура выбора роли"""
    keyboard = [
        [InlineKeyboardButton("Водитель", callback_data="role_driver")],
        [InlineKeyboardButton("Логист", callback_data="role_logist")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_contact_inline_keyboard():
    """Клавиатура для контакта"""
    keyboard = [
        [InlineKeyboardButton("Как поделиться контактом", callback_data="contact_help")],
        [InlineKeyboardButton("Назад", callback_data="back_to_roles")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_inline_keyboard():
    """Главная админ клавиатура"""
    keyboard = [
        [InlineKeyboardButton("Автомобили", callback_data="admin_cars_section")],
        [InlineKeyboardButton("Сотрудники", callback_data="admin_employees_section")],
        [InlineKeyboardButton("Смены", callback_data="admin_shifts_section")],
        [InlineKeyboardButton("Отчеты", callback_data="admin_reports_section")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_cars_keyboard():
    """Клавиатура раздела автомобили"""
    keyboard = [
        [InlineKeyboardButton("Добавить автомобиль", callback_data="add_car")],
        [InlineKeyboardButton("Редактировать автомобиль", callback_data="cars_list_edit")],
        [InlineKeyboardButton("Удалить автомобиль", callback_data="cars_list_delete")],
        [InlineKeyboardButton("Список автомобилей", callback_data="cars_list_view")],
        [InlineKeyboardButton("Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manage_cars_keyboard():
    """Клавиатура управления автомобилями"""
    keyboard = [
        [InlineKeyboardButton("Добавить автомобиль", callback_data="add_car")],
        [InlineKeyboardButton("Список автомобилей", callback_data="cars_list_view")],
        [InlineKeyboardButton("Редактировать автомобиль", callback_data="cars_list_edit")],
        [InlineKeyboardButton("Удалить автомобиль", callback_data="cars_list_delete")],
        [InlineKeyboardButton("Назад", callback_data="admin_cars_section")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_employees_keyboard():
    """Клавиатура раздела сотрудники"""
    keyboard = [
        [InlineKeyboardButton("Управление водителями", callback_data="manage_drivers")],
        [InlineKeyboardButton("Управление логистами", callback_data="manage_logists")],
        [InlineKeyboardButton("Статистика по сотрудникам", callback_data="employees_stats")],
        [InlineKeyboardButton("Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_shifts_keyboard():
    """Клавиатура раздела смены"""
    keyboard = [
        [InlineKeyboardButton("Активные смены", callback_data="show_active_shifts")],
        [InlineKeyboardButton("История смен", callback_data="shifts_history")],
        [InlineKeyboardButton("Статистика смен", callback_data="shifts_stats")],
        [InlineKeyboardButton("Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_reports_keyboard():
    """Клавиатура раздела отчеты"""
    keyboard = [
        [InlineKeyboardButton("Общая статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("Отчет по сменам", callback_data="shifts_report")],
        [InlineKeyboardButton("Отчет по машинам", callback_data="cars_report")],
        [InlineKeyboardButton("Отчет по сотрудникам", callback_data="employees_report")],
        [InlineKeyboardButton("Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Клавиатура с кнопкой назад"""
    keyboard = [["Назад"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_cancel_keyboard():
    """Клавиатура с кнопкой отмены"""
    keyboard = [
        ["Отменить"],
        ["Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_chat_menu():
    """Клавиатура для чата"""
    keyboard = [
        ["Написать сообщение", "Обновить"],
        ["Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_chat_keyboard():
    """Клавиатура для чата"""
    keyboard = [
        ["Написать сообщение", "Обновить"],
        ["Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_manage_drivers_keyboard():
    """Клавиатура управления водителями"""
    keyboard = [
        [InlineKeyboardButton("Добавить водителя", callback_data="add_driver")],
        [InlineKeyboardButton("Редактировать водителя", callback_data="edit_driver_list")],
        [InlineKeyboardButton("Удалить водителя", callback_data="delete_driver_list")],
        [InlineKeyboardButton("Назад", callback_data="admin_employees_section")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_manage_logists_keyboard():
    """Клавиатура управления логистами"""
    keyboard = [
        [InlineKeyboardButton("Добавить логиста", callback_data="add_logist")],
        [InlineKeyboardButton("Редактировать логиста", callback_data="edit_logist_list")],
        [InlineKeyboardButton("Удалить логиста", callback_data="delete_logist_list")],
        [InlineKeyboardButton("Назад", callback_data="admin_employees_section")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_keyboard():
    """Клавиатура подтверждения"""
    keyboard = [
        [InlineKeyboardButton("Подтвердить", callback_data="confirm")],
        [InlineKeyboardButton("Отменить", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_user_list_keyboard(users, action_type):
    """Клавиатура со списком пользователей"""
    keyboard = []

    for user in users:
        if action_type == "edit_driver":
            callback_data = f"edit_driver_{user.id}"
        elif action_type == "delete_driver":
            callback_data = f"delete_driver_{user.id}"
        elif action_type == "edit_logist":
            callback_data = f"edit_logist_{user.id}"
        elif action_type == "delete_logist":
            callback_data = f"delete_logist_{user.id}"
        else:
            callback_data = f"view_user_{user.id}"

        keyboard.append([InlineKeyboardButton(f"{user.name} ({user.phone})", callback_data=callback_data)])

    if action_type.startswith("edit_driver") or action_type.startswith("delete_driver"):
        keyboard.append([InlineKeyboardButton("Назад", callback_data="manage_drivers")])
    elif action_type.startswith("edit_logist") or action_type.startswith("delete_logist"):
        keyboard.append([InlineKeyboardButton("Назад", callback_data="manage_logists")])
    else:
        keyboard.append([InlineKeyboardButton("Назад", callback_data="admin_employees_section")])

    return InlineKeyboardMarkup(keyboard)

def get_car_list_keyboard(cars, action_type):
    """Клавиатура со списком автомобилей"""
    keyboard = []

    for car in cars:
        car_name = car.number
        if car.brand:
            car_name += f" ({car.brand}"
            if car.model:
                car_name += f" {car.model}"
            car_name += ")"

        if action_type == "edit":
            callback_data = f"edit_car_{car.id}"
        elif action_type == "delete":
            callback_data = f"delete_car_{car.id}"
        else:
            callback_data = f"view_car_{car.id}"

        keyboard.append([InlineKeyboardButton(car_name, callback_data=callback_data)])

    keyboard.append([InlineKeyboardButton("Назад", callback_data="admin_cars_section")])
    return InlineKeyboardMarkup(keyboard)

def get_edit_car_keyboard(car_id):
    """Клавиатура для редактирования автомобиля"""
    keyboard = [
        [InlineKeyboardButton("Номер", callback_data=f"number_edit_{car_id}")],
        [InlineKeyboardButton("Марка", callback_data=f"brand_edit_{car_id}")],
        [InlineKeyboardButton("Модель", callback_data=f"model_edit_{car_id}")],
        [InlineKeyboardButton("Топливо", callback_data=f"fuel_edit_{car_id}")],
        [InlineKeyboardButton("Пробег", callback_data=f"mileage_edit_{car_id}")],
        [InlineKeyboardButton("Назад", callback_data="admin_cars_section")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_edit_user_keyboard(user_id, user_type):
    """Клавиатура для редактирования пользователя"""
    keyboard = [
        [InlineKeyboardButton("Имя", callback_data=f"name_edit_{user_type}_{user_id}")],
        [InlineKeyboardButton("Телефон", callback_data=f"phone_edit_{user_type}_{user_id}")],
        [InlineKeyboardButton("Назад", callback_data=f"manage_{user_type}s")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_driver_menu():
    """Главное меню водителя"""
    keyboard = [
        [InlineKeyboardButton("Начать смену", callback_data="start_shift")],
        [InlineKeyboardButton("Завершить смену", callback_data="end_shift")],
        [InlineKeyboardButton("Чат", callback_data="open_chat")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_logist_menu():
    """Главное меню логиста"""
    keyboard = [
        [InlineKeyboardButton("Маршруты", callback_data="show_route")],
        [InlineKeyboardButton("Доставки", callback_data="delivery_list")],
        [InlineKeyboardButton("Отчет смен", callback_data="shifts_report")],
        [InlineKeyboardButton("Чат", callback_data="open_chat")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_chat_inline_keyboard():
    """Inline клавиатура для чата"""
    keyboard = [
        [InlineKeyboardButton("Написать сообщение", callback_data="write_message")],
        [InlineKeyboardButton("Обновить", callback_data="refresh_chat")],
        [InlineKeyboardButton("Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_cancel_write_keyboard():
    """Клавиатура отмены написания сообщения"""
    keyboard = [
        [InlineKeyboardButton("Отменить", callback_data="cancel_writing")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_driver_dialog_keyboard():
    """Диалоговая клавиатура водителя"""
    keyboard = [
        [InlineKeyboardButton("Начать смену", callback_data="start_shift")],
        [InlineKeyboardButton("Завершить смену", callback_data="end_shift")],
        [InlineKeyboardButton("Чат", callback_data="open_chat")],
        [InlineKeyboardButton("Назад", callback_data="back_to_roles")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_logist_dialog_keyboard():
    """Диалоговая клавиатура логиста"""
    keyboard = [
        [InlineKeyboardButton("Маршруты", callback_data="show_route")],
        [InlineKeyboardButton("Доставки", callback_data="delivery_list")],
        [InlineKeyboardButton("Отчет смен", callback_data="shifts_report")],
        [InlineKeyboardButton("Чат", callback_data="open_chat")],
        [InlineKeyboardButton("Назад", callback_data="back_to_roles")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_shift_start_keyboard():
    """Клавиатура начала смены"""
    keyboard = [
        [InlineKeyboardButton("Выбрать автомобиль", callback_data="select_car_for_shift")],
        [InlineKeyboardButton("Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_writing_message_keyboard():
    """Клавиатура для написания сообщения"""
    keyboard = [
        [InlineKeyboardButton("Отменить", callback_data="cancel_writing")]
    ]
    return InlineKeyboardMarkup(keyboard)