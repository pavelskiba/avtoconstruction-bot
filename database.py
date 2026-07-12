import aiosqlite

from config import DB_PATH

STATE_NEW = "new"
STATE_WAITING_SUBSCRIBE = "waiting_subscribe"
STATE_VIDEO_SENT = "video_sent"
STATE_GUIDE_SENT = "guide_sent"
STATE_AWAITING_PAYMENT = "awaiting_payment"
STATE_PAID = "paid"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                state TEXT NOT NULL DEFAULT 'new',
                course_step INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        await conn.commit()


async def get_user(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cur = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        if row is not None:
            return dict(row)

        await conn.execute(
            "INSERT INTO users (user_id, state) VALUES (?, ?)", (user_id, STATE_NEW)
        )
        await conn.commit()
        return {"user_id": user_id, "state": STATE_NEW, "course_step": 0}


async def set_state(user_id: int, state: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE users SET state = ? WHERE user_id = ?", (state, user_id)
        )
        await conn.commit()


async def set_course_step(user_id: int, step: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE users SET course_step = ? WHERE user_id = ?", (step, user_id)
        )
        await conn.commit()
