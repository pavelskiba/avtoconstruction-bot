import asyncio
import logging

from aiohttp import web

import config
import database as db
import payments
from funnel import grant_course_access

log = logging.getLogger("avtoconstruction_bot.webhook")


async def handle_yookassa_webhook(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except ValueError:
        return web.Response(status=400)

    payment_id = data.get("object", {}).get("id")
    if not payment_id:
        return web.Response(status=400)

    # Тело уведомления не проверяется на подлинность - запрашиваем реальный
    # статус платежа по его id через API ЮKassa, доверяем только этому ответу.
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
    user = await db.get_user(user_id)
    if user["state"] == db.STATE_PAID:
        return web.Response(status=200)  # уже выдали доступ, повторное уведомление игнорируем

    await grant_course_access(user_id)
    return web.Response(status=200)


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_post(config.WEBHOOK_PATH, handle_yookassa_webhook)
    return app
