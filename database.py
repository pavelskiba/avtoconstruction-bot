import aiosqlite

from config import DB_PATH

STATE_NEW = "new"
STATE_WAITING_SUBSCRIBE = "waiting_subscribe"
STATE_GUIDE_SENT = "guide_sent"
STATE_PAID = "paid"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                state TEXT NOT NULL DEFAULT 'new'
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_payments (
                payment_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL
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
        return {"user_id": user_id, "state": STATE_NEW}


async def set_state(user_id: int, state: str):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE users SET state = ? WHERE user_id = ?", (state, user_id)
        )
        await conn.commit()


async def mark_payment_processed(payment_id: str, user_id: int) -> bool:
    """Атомарно фиксирует payment_id как обработанный.

    Возвращает True, только если запись создана этим вызовом впервые —
    так повторные уведомления ЮKassa не приводят к повторной отправке
    материалов курса.
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        try:
            await conn.execute(
                "INSERT INTO processed_payments (payment_id, user_id) VALUES (?, ?)",
                (payment_id, user_id),
            )
            await conn.commit()
            return True
        except aiosqlite.IntegrityError:
            return False
