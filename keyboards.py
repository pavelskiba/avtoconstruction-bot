from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def subscribe_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Я подписался", callback_data="check_subscription")]
        ]
    )


def sale_keyboard(payment_url: str, landing_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url=payment_url)],
            [InlineKeyboardButton(text="Информация о курсе", url=landing_url)],
        ]
    )
