import asyncio
import logging

from aiohttp import web

import config
import database as db
import payments
from telegram_client import bot

log = logging.getLogger("avtoconstruction_bot.webhook")


async def handle_yookassa_webhook(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except ValueError:
        return web.Response(status=400)

    payment_id = data.get("object", {}).get("id")
    if not payment_id:
        return web.Response(status=400)

    # Телу уведомления не доверяем — запрашиваем реальный статус платежа
    # по его id через API ЮKassa.
    try:
        payment = await asyncio.to_thread(payments.get_payment, payment_id)
    except Exception:
        log.exception("Failed to fetch payment %s from YooKassa", payment_id)
        return web.Response(status=502)

    if payment.status != "succeeded" or not payment.paid:
        return web.Response(status=200)

    user_id_raw = (payment.metadata or {}).get("telegram_user_id")
    if not user_id_raw:
        log.warning("Payment %s has no telegram_user_id in metadata", payment_id)
        return web.Response(status=200)

    user_id = int(user_id_raw)

    is_new = await db.mark_payment_processed(payment_id, user_id)
    if not is_new:
        return web.Response(status=200)  # уведомление повторное, материалы уже отправлены

    await db.set_state(user_id, db.STATE_PAID)

    try:
        await bot.send_message(user_id, config.COURSE_MATERIALS_TEXT)
    except Exception:
        log.exception("Failed to send course materials to %s", user_id)

    return web.Response(status=200)


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_post(config.WEBHOOK_PATH, handle_yookassa_webhook)
    return app
