import uuid

from yookassa import Configuration, Payment

import config

Configuration.account_id = config.YOOKASSA_SHOP_ID
Configuration.secret_key = config.YOOKASSA_SECRET_KEY


def create_payment(user_id: int) -> str:
    payment = Payment.create(
        {
            "amount": {
                "value": config.PAYMENT_AMOUNT,
                "currency": config.PAYMENT_CURRENCY,
            },
            "confirmation": {
                "type": "redirect",
                "return_url": config.PAYMENT_RETURN_URL,
            },
            "capture": True,
            "description": config.PAYMENT_DESCRIPTION,
            "metadata": {"telegram_user_id": str(user_id)},
        },
        uuid.uuid4(),
    )
    return payment.confirmation.confirmation_url


def get_payment(payment_id: str) -> Payment:
    return Payment.find_one(payment_id)
