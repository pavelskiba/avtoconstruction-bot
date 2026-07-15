import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "ВСТАВЬ_СЮДА_ТОКЕН")

CHANNEL_USERNAME = "@rabochye_prosto"
CHANNEL_ID = -1003716790314

LANDING_URL = "https://majestic-crumble-f5f364.netlify.app/"

# Вводное бесплатное видео (ссылка на YouTube)
INTRO_VIDEO_URL = "https://youtube.com/shorts/lLnLt4K5PSI?si=e2O0YZIbw-PLMqVF"

# Сообщение с материалами курса — отправляется после подтверждённой оплаты
COURSE_MATERIALS_TEXT = (
    "Оплата прошла успешно! 🎉 Вот материалы курса:\n\n"
    "1. [НАЗВАНИЕ] — [ССЫЛКА]\n"
    "2. [НАЗВАНИЕ] — [ССЫЛКА]\n"
    "3. [НАЗВАНИЕ] — [ССЫЛКА]"
)

TRIGGER_WORDS = ("тендер", "смета")

# Пауза между приветствием и запросом на подписку (в секундах), чтобы бот
# не слал всё разом одной пачкой
WELCOME_TO_SUBSCRIBE_DELAY = 2

# На Railway укажи переменную DB_PATH на путь внутри примонтированного
# Volume (например /data/bot.db) - иначе база будет стираться при каждом деплое
DB_PATH = os.environ.get("DB_PATH", "bot.db")

# --- ЮKassa ---
# Бот сам создаёт платёж через API (та же страница оплаты ЮKassa, что и
# раньше, просто генерируется на конкретного пользователя) — это даёт
# возможность привязать платёж к telegram_user_id через metadata и потом
# автоматически проверить его статус по вебхуку.
YOOKASSA_SHOP_ID = os.environ.get("YOOKASSA_SHOP_ID", "")
YOOKASSA_SECRET_KEY = os.environ.get("YOOKASSA_SECRET_KEY", "")

PAYMENT_AMOUNT = "990.00"
PAYMENT_CURRENCY = "RUB"
PAYMENT_DESCRIPTION = "Доступ к мини-курсу по созданию ИИ ботов для строительства"

# Куда ЮKassa вернёт пользователя после оплаты (страница-квитанция)
PAYMENT_RETURN_URL = LANDING_URL

# HTTP-эндпоинт, принимающий уведомления от ЮKassa (настраивается в личном
# кабинете ЮKassa: Настройки -> HTTP-уведомления -> https://<домен>/yookassa/webhook)
WEBHOOK_PATH = "/yookassa/webhook"
WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.environ.get("PORT", os.environ.get("WEBHOOK_PORT", "8080")))
