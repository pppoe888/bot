
import os

# Токен от @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

# ID администратора (ваш Telegram ID)
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

# URL базы данных
DATABASE_URL = "sqlite:///bot.db"
