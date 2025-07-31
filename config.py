
import os

# Токен от @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# ID администратора (ваш Telegram ID)
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
if ADMIN_ID == 0:
    raise ValueError("ADMIN_ID не установлен в переменных окружения")

# Настройки базы данных
DATABASE_URL = "sqlite:///bot.db"
