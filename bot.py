import asyncio
import logging

from aiogram import F
from aiogram.exceptions import TelegramAPIError
from aiogram.enums import ChatMemberStatus
from aiogram.types import CallbackQuery, Message
from aiohttp import web

import config
import database as db
import webhook_server
from telegram_client import bot, dp
from funnel import send_course_video
from keyboards import subscribe_keyboard, sale_keyboard

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("avtoconstruction_bot")

SUBSCRIBED_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


def subscribe_request_text() -> str:
    return (
        "Отлично! Чтобы получить доступ к бесплатному видео и материалам, "
        f"подпишись на наш канал: {config.CHANNEL_USERNAME}\n"
        "Затем нажми кнопку «Я подписался», и я пришлю тебе ссылку."
    )


@dp.callback_query(F.data == "course_next")
async def handle_course_next(callback: CallbackQuery):
    await callback.answer()
    user = await db.get_user(callback.from_user.id)
    step = user["course_step"]
    if step >= len(config.COURSE_VIDEOS):
        return
    await send_course_video(callback.from_user.id, step)


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

    await db.set_state(callback.from_user.id, db.STATE_GUIDE_SENT)

    await callback.message.answer(
        "Спасибо за подписку! 🎉 Вот твое бесплатное вводное видео — посмотри, "
        "чтобы разобраться в основах смет и тендеров. 📹\n\n"
        f"{config.INTRO_VIDEO_URL}\n\n"
        f"А вот и полезный гайд, который поможет закрепить материал: {config.GUIDE_PLACEHOLDER}\n\n"
        "Хочешь узнать больше, как выигрывать тендеры и экономить на сметах? Жми на кнопку ниже 👇",
        reply_markup=sale_keyboard(config.LANDING_URL),
    )


# --- триггер по ключевым словам (регистрируем последним - "catch-all" по тексту) ---
@dp.message(F.text)
async def handle_text(message: Message):
    text = message.text.lower()
    if not any(word in text for word in config.TRIGGER_WORDS):
        return

    user = await db.get_user(message.from_user.id)

    if user["state"] == db.STATE_NEW:
        await message.answer(
            "Привет! Хочешь научиться составлять сметы и выигрывать тендеры? "
            "Начни с бесплатного видео. Просто напиши «смета» или «тендер»."
        )
        await asyncio.sleep(config.WELCOME_TO_SUBSCRIBE_DELAY)

    if user["state"] in (db.STATE_NEW, db.STATE_WAITING_SUBSCRIBE):
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
    log.info("Webhook server listening on %s:%s%s", config.WEBHOOK_HOST, config.WEBHOOK_PORT, config.WEBHOOK_PATH)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
