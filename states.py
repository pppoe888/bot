# Состояния
(
    WAITING_PHONE,
    ADDING_DRIVER_PHONE,
    ADDING_DRIVER_NAME,
    ADDING_CAR_NUMBER,
    ADDING_CAR_BRAND,
    ADDING_CAR_MODEL,
    ADDING_CAR_FUEL,
    ADDING_CAR_MILEAGE,
    CHOOSING_CAR,
    ENTERING_START_MILEAGE,
    TAKING_ODOMETER_PHOTO,
    TAKING_FUEL_PHOTOS,
    TAKING_OIL_PHOTO,
    TAKING_CABIN_PHOTO,
    ENTERING_END_MILEAGE,
    TAKING_END_ODOMETER_PHOTO,
) = range(16)

# Состояния для пользователей
WAITING_PHONE = "waiting_phone"
WAITING_DRIVER_NAME = "waiting_driver_name"
WAITING_CAR_DATA = "waiting_car_data"

# Состояния админки
ADDING_DRIVER = "adding_driver"
ADDING_CAR = "adding_car"
EDITING_DRIVER = "editing_driver"
EDITING_CAR = "editing_car"

# Состояния смен
CHOOSING_CAR = "choosing_car"
ENTERING_START_MILEAGE = "entering_start_mileage"
ENTERING_END_MILEAGE = "entering_end_mileage"