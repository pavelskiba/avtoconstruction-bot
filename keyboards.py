from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def subscribe_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Я подписался", callback_data="check_subscription")]
        ]
    )


def sale_keyboard(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Ознакомиться подробнее", url=url)]]
    )
