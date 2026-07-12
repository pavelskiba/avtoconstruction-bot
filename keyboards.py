from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def subscribe_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Я подписался", callback_data="check_subscription")]
        ]
    )


def sale_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Ознакомиться подробнее", callback_data="get_payment_link")]
        ]
    )


def payment_link_keyboard(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Оплатить 990₽", url=url)]])


def next_video_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Далее", callback_data="course_next")]]
    )
