# Avtoconstruction Bot

Воронка для @Avtoconstruction_bot: триггер по словам "смета"/"тендер" →
проверка подписки на канал → выдача бесплатного видео → гайд → персональная
ссылка на оплату ЮKassa → после реальной оплаты (по вебхуку) — видео курса
по одному с кнопкой «Далее».

Никаких команд для человека нет — всё происходит автоматически по мере
переписки пользователя с ботом.

## Установка

```
pip install -r requirements.txt
```

## Настройка

Данные лежат в `.env` (уже заполнен, кроме токена бота) и `config.py`:

- `.env` → `BOT_TOKEN` — токен из @BotFather.
- `.env` → `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY` — уже вписаны.
- Остальное (канал, ссылки на видео, текст-заглушка гайда, суммы) — в `config.py`.

`.env` в `.gitignore` — не публикуйте и не коммитьте этот файл, в нём боевой
секретный ключ ЮKassa.

## Запуск

```
python bot.py
```

Поднимет и long-polling бота, и HTTP-сервер для приёма вебхуков от ЮKassa
на порту `WEBHOOK_PORT` (по умолчанию 8080, либо `PORT`, если хостинг сам
его подставляет).

## Деплой на Railway

1. Установи Railway CLI и залогинься:
   ```
   npm i -g @railway/cli
   railway login
   ```
2. В папке проекта (`avtoconstruction_bot`) создай и привяжи проект:
   ```
   railway init
   ```
3. **Volume для базы** (иначе `bot.db` будет стираться при каждом деплое):
   в Railway → твой сервис → вкладка **Volumes** → Add Volume → примонтируй,
   например, на `/data`.
4. Задай переменные окружения (Railway → Variables, или через CLI):
   ```
   railway variables set BOT_TOKEN=токен_из_BotFather
   railway variables set YOOKASSA_SHOP_ID=1362304
   railway variables set YOOKASSA_SECRET_KEY=live_pHkwaV1p8YU6uRxxDYYQBlXp0_gOxzrPKt8yMGMwT8g
   railway variables set DB_PATH=/data/bot.db
   ```
   (`PORT` Railway подставляет сам — трогать не нужно, `config.py` уже это учитывает).
5. Деплой:
   ```
   railway up
   ```
6. Включи публичный домен: сервис → Settings → Networking → **Generate Domain**.
   Получишь адрес вида `https://xxxx.up.railway.app` — это и есть публичный
   HTTPS-адрес бота для вебхука.
7. Пропиши этот адрес в ЮKassa (см. следующий раздел).

`.env` на Railway не нужен и не используется — там свои Variables, задавай
через них. Локальный `.env` остаётся только для запуска на своём компьютере.

## Настройка вебхука в ЮKassa

В личном кабинете ЮKassa: Настройки → HTTP-уведомления → указать
`https://xxxx.up.railway.app/yookassa/webhook` (свой домен из Railway),
событие `payment.succeeded`.

Бот не доверяет телу уведомления напрямую — при получении вебхука он
дополнительно запрашивает статус платежа через API ЮKassa и только после
этого выдаёт доступ к курсу.

## Логика состояний пользователя

Хранится в SQLite (`bot.db`), поле `state`:

`new` → `waiting_subscribe` → `video_sent` → `guide_sent` → `awaiting_payment` → `paid`

Плюс `course_step` — номер следующего видео курса (0..3).
