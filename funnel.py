import config
import database as db
from telegram_client import bot
from keyboards import next_video_keyboard


async def send_course_video(chat_id: int, step: int):
    is_last = step == len(config.COURSE_VIDEOS) - 1
    keyboard = None if is_last else next_video_keyboard()
    await bot.send_message(
        chat_id,
        f"Видео {step + 1} из {len(config.COURSE_VIDEOS)}: {config.COURSE_VIDEOS[step]}",
        reply_markup=keyboard,
    )
    await db.set_course_step(chat_id, step + 1)


async def grant_course_access(user_id: int):
    await db.set_state(user_id, db.STATE_PAID)
    await db.set_course_step(user_id, 0)
    await send_course_video(user_id, 0)
