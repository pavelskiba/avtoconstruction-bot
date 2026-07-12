import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "ВСТАВЬ_СЮДА_ТОКЕН")

CHANNEL_USERNAME = "@rabochye_prosto"
CHANNEL_ID = -1003716790314

LANDING_URL = "https://majestic-crumble-f5f364.netlify.app/"

# Вводное бесплатное видео (ссылка на YouTube)
INTRO_VIDEO_URL = "https://youtube.com/shorts/lLnLt4K5PSI?si=e2O0YZIbw-PLMqVF"

GUIDE_PLACEHOLDER = "[ГАЙД]"

TRIGGER_WORDS = ("тендер", "смета")

# Пауза между приветствием и запросом на подписку (в секундах), чтобы бот
# не слал всё разом одной пачкой
WELCOME_TO_SUBSCRIBE_DELAY = 2

# На Railway укажи переменную DB_PATH на путь внутри примонтированного
# Volume (например /data/bot.db) - иначе база будет стираться при каждом деплое
DB_PATH = os.environ.get("DB_PATH", "bot.db")
