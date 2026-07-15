# Avtoconstruction Bot

Воронка для @Avtoconstruction_bot:

1. Триггер по словам "смета"/"тендер" (без учёта регистра) → приветствие.
2. Запрос на подписку на канал с кнопкой «Я подписался».
3. Проверка подписки через Telegram API (`getChatMember`). Не подписан —
   повторяет запрос. Подписан — присылает вводное видео и просит email
   (нужен для электронного чека по 54-ФЗ).
4. После получения валидного email бот создаёт платёж через ЮKassa API
   (`payments.create_payment`) с `metadata.telegram_user_id` (чтобы потом
   связать оплату с конкретным пользователем Telegram) и данными чека
   (`receipt.customer.email`, `receipt.items` с `vat_code` из
   `config.PAYMENT_VAT_CODE`). Присылает две кнопки — «Оплатить» (ссылка
   на платёж, 990 ₽) и «Информация о курсе» (лендинг). Если email уже
   известен (сохранён от прошлой попытки), шаг запроса пропускается.
5. ЮKassa шлёт вебхук на `/yookassa/webhook`. Бот **не доверяет телу
   уведомления** — переспрашивает реальный статус платежа через API
   ЮKassa по `payment_id`, и только если `status == succeeded` и
   `paid == True`, отправляет пользователю сообщение с материалами курса
   (`config.COURSE_MATERIALS_TEXT`). Повторные уведомления по уже
   обработанному `payment_id` игнорируются (таблица `processed_payments`).

## Установка

```
pip install -r requirements.txt
```

## Настройка

- `.env` → `BOT_TOKEN` — токен бота (уже вписан), `YOOKASSA_SHOP_ID`,
  `YOOKASSA_SECRET_KEY` — данные из личного кабинета ЮKassa (Настройки →
  API-ключи).
- Остальное (канал, ссылка на видео, лендинг, сумма/описание платежа,
  текст с материалами курса) — в `config.py`.

`.env` в `.gitignore` — не публикуйте и не коммитьте этот файл.

## Запуск

```
python bot.py
```

## Деплой на Railway

1. Установи Railway CLI и залогинься:
   ```
   npm i -g @railway/cli
   railway login
   ```
2. Подключи сервис к GitHub-репозиторию проекта (Source → GitHub Repo).
3. **Volume для базы** (иначе `bot.db` будет стираться при каждом деплое):
   на канвасе проекта → ПКМ по сервису → **Attach Volume** → Mount Path `/data`.
4. Задай переменные окружения (Variables):
   ```
   BOT_TOKEN=токен_из_BotFather
   DB_PATH=/data/bot.db
   YOOKASSA_SHOP_ID=...
   YOOKASSA_SECRET_KEY=...
   ```
5. **Публичный домен обязателен** (Networking → Generate Domain) — на него
   ЮKassa шлёт вебхук. В личном кабинете ЮKassa: Настройки → HTTP-уведомления
   → `https://<домен>/yookassa/webhook`.
6. Деплой произойдёт автоматически при пуше в GitHub (или `railway up`).

## Логика состояний пользователя

Хранится в SQLite (`bot.db`), поле `state`:

`new` → `waiting_subscribe` → `waiting_email` → `guide_sent` → `paid`

Email сохраняется в поле `email` — при повторном заходе в оплату уже не
запрашивается.
