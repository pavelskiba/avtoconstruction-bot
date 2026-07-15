import asyncio
import logging
import re

from aiogram import F
from aiogram.exceptions import TelegramAPIError
from aiogram.enums import ChatMemberStatus
from aiogram.types import CallbackQuery, LinkPreviewOptions, Message
from aiohttp import web

import config
import database as db
import payments
import webhook_server
from telegram_client import bot, dp
from keyboards import subscribe_keyboard, sale_keyboard

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("avtoconstruction_bot")

SUBSCRIBED_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def subscribe_request_text() -> str:
    return (
        "Отлично! Чтобы получить доступ к бесплатному видео и материалам, "
        f"подпишись на наш канал: {config.CHANNEL_USERNAME}\n"
        "Затем нажми кнопку «Я подписался», и я пришлю тебе ссылку."
    )


@dp.callback_query(F.data == "check_subscription")
async def handle_check_subscription(callback: CallbackQuery):
    await callback.answer()

    try:
        member = await bot.get_chat_member(
            chat_id=config.CHANNEL_ID, user_id=callback.from_user.id
        )
    except TelegramAPIError as e:
        log.warning("get_chat_member failed for %s: %s", callback.from_user.id, e)
        await callback.message.answer(
            "Не получилось проверить подписку, попробуй ещё раз чуть позже."
        )
        return

    if member.status not in SUBSCRIBED_STATUSES:
        await callback.message.answer(
            subscribe_request_text(), reply_markup=subscribe_keyboard()
        )
        return

    user = await db.get_user(callback.from_user.id)

    await callback.message.answer(
        "Спасибо за подписку! 🎉 Вот твое бесплатное вводное видео — посмотри, "
        "чтобы разобраться в основах смет и тендеров. 📹\n\n"
        f"{config.INTRO_VIDEO_URL}\n\n"
        "А вот и полезный гайд, который поможет закрепить материал:",
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )

    if user["email"]:
        await send_payment_offer(callback.message.chat.id, callback.from_user.id, user["email"])
        return

    await db.set_state(callback.from_user.id, db.STATE_WAITING_EMAIL)
    await callback.message.answer(
        "Хочешь узнать больше, как выигрывать тендеры и экономить на сметах, и получить "
        "доступ к курсу? Напиши свой email, отправлю всю информацию о курсе"
    )


async def send_payment_offer(chat_id: int, user_id: int, email: str):
    try:
        payment_url = await asyncio.to_thread(payments.create_payment, user_id, email)
    except Exception:
        log.exception("Failed to create payment for %s", user_id)
        await bot.send_message(
            chat_id,
            "Не получилось подготовить ссылку на оплату, попробуй ещё раз чуть позже "
            "— просто нажми ещё раз на кнопку «Я подписался».",
        )
        return

    await db.set_state(user_id, db.STATE_GUIDE_SENT)
    await bot.send_message(
        chat_id,
        "Отлично! Снизу две кнопки, по одной можешь узнать всю информацию о курсе, "
        "а по другой его оплатить",
        reply_markup=sale_keyboard(payment_url, config.LANDING_URL),
    )


# --- триггер по ключевым словам (регистрируем последним - "catch-all" по тексту) ---
@dp.message(F.text)
async def handle_text(message: Message):
    user = await db.get_user(message.from_user.id)

    if user["state"] == db.STATE_WAITING_EMAIL:
        email = message.text.strip()
        if not EMAIL_RE.match(email):
            await message.answer(
                "Похоже, это не email. Напиши в формате name@example.com"
            )
            return
        await db.set_email(message.from_user.id, email)
        await send_payment_offer(message.chat.id, message.from_user.id, email)
        return

    text = message.text.lower()
    if not any(word in text for word in config.TRIGGER_WORDS):
        return

    await message.answer(
        "Привет! 👷‍♂️ Хочешь научиться составлять сметы и выигрывать тендеры? "
        "Начни с бесплатного видео — дальше вся инфа"
    )
    await asyncio.sleep(config.WELCOME_TO_SUBSCRIBE_DELAY)

    await db.set_state(message.from_user.id, db.STATE_WAITING_SUBSCRIBE)
    await message.answer(subscribe_request_text(), reply_markup=subscribe_keyboard())


async def main():
    await db.init_db()
    await bot.delete_webhook(drop_pending_updates=True)

    app = webhook_server.create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, config.WEBHOOK_HOST, config.WEBHOOK_PORT)
    await site.start()
    log.info(
        "Webhook server listening on %s:%s%s",
        config.WEBHOOK_HOST, config.WEBHOOK_PORT, config.WEBHOOK_PATH,
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
