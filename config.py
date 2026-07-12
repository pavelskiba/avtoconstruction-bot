import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "ВСТАВЬ_СЮДА_ТОКЕН")

CHANNEL_USERNAME = "@rabochye_prosto"
CHANNEL_ID = -1003716790314

LANDING_URL = "https://majestic-crumble-f5f364.netlify.app/"

# Вводное бесплатное видео (ссылка на YouTube)
INTRO_VIDEO_URL = "https://youtube.com/shorts/lLnLt4K5PSI?si=e2O0YZIbw-PLMqVF"

# Видео курса, выдаются по одному после оплаты
COURSE_VIDEOS = [
    "https://youtube.com/shorts/eqEeoZWqka8",
    "https://youtube.com/shorts/UwNTnfosRdA",
    "https://youtube.com/shorts/m-cldLR7AQ8",
]

GUIDE_PLACEHOLDER = "[ГАЙД]"

TRIGGER_WORDS = ("тендер", "смета")

# Пауза между приветствием и запросом на подписку (в секундах), чтобы бот
# не слал всё разом одной пачкой
WELCOME_TO_SUBSCRIBE_DELAY = 2

# На Railway укажи переменную DB_PATH на путь внутри примонтированного
# Volume (например /data/bot.db) - иначе база будет стираться при каждом деплое
DB_PATH = os.environ.get("DB_PATH", "bot.db")

# --- ЮKassa ---
YOOKASSA_SHOP_ID = os.environ.get("YOOKASSA_SHOP_ID", "")
YOOKASSA_SECRET_KEY = os.environ.get("YOOKASSA_SECRET_KEY", "")

PAYMENT_AMOUNT = "990.00"
PAYMENT_CURRENCY = "RUB"
PAYMENT_DESCRIPTION = "Доступ к курсу «Как выигрывать тендеры и экономить на сметах»"

# Куда ЮKassa вернёт пользователя после оплаты (страница-квитанция)
PAYMENT_RETURN_URL = LANDING_URL

# HTTP-сервер, принимающий уведомления от ЮKassa (настраивается в личном
# кабинете ЮKassa: Настройки -> HTTP-уведомления -> https://<host>/yookassa/webhook)
WEBHOOK_PATH = "/yookassa/webhook"
WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.environ.get("PORT", os.environ.get("WEBHOOK_PORT", "8080")))
