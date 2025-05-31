import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Union

DB_PATH = Path("/bot/database/subscriptions.sqlite")

async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
                                user_id TEXT PRIMARY KEY,
                                username TEXT,
                                expire INTEGER,
                                trial BOOLEAN DEFAULT 0
                             )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS payments (
                                payment_id TEXT PRIMARY KEY,
                                user_id TEXT,
                                amount INTEGER,
                                date TEXT,
                                status TEXT,
                                payment_yoo_id TEXT
                             )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS referrals (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                referrer_user_id TEXT NOT NULL,
                                referral_user_id TEXT UNIQUE NOT NULL,
                                used BOOLEAN DEFAULT FALSE,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                             )''')
        await db.commit()


async def add_user_to_db(user_id: str, username: str, expire: int, trial: bool) -> None:
    """
    Добавляет пользователя в базу данных или обновляет его данные, если он уже существует.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO users (user_id, username, expire, trial) 
            VALUES (?, ?, ?, ?) 
            ON CONFLICT(user_id) DO UPDATE 
            SET username = excluded.username,
                expire = excluded.expire,
                trial = excluded.trial
        ''', (user_id, username, expire, trial))
        await db.commit()


async def user_use_trial_to_db(user_id: str) -> None:
    """
    Устанавливает флаг trial для пользователя в базе данных.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE users SET trial = 1 WHERE user_id = ?', (user_id,))
        await db.commit()


async def check_user_trial(user_id: str) -> bool:
    """
    Проверяет, использовал ли пользователь пробный период.
    Возвращает True, если пробный период использован, иначе False.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT trial FROM users WHERE user_id = ?', (user_id,))
        trial = await cursor.fetchone()
        return bool(trial and trial[0] == 1)


async def add_payment_to_db(payment_id: str, user_id: str, amount: int, status: str, payment_yoo_id: str) -> None:
    """
    Добавляет информацию о платеже в базу данных.
    """
    now = datetime.now().isoformat(sep=' ', timespec='seconds')
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO payments (payment_id, user_id, amount, date, status, payment_yoo_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (payment_id, user_id, amount, now, status, payment_yoo_id))
        await db.commit()


async def update_payment_status(payment_yoo_id: str, status: str) -> None:
    """
    Обновляет статус платежа в базе данных.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE payments SET status = ? WHERE payment_yoo_id = ?', (status, payment_yoo_id))
        await db.commit()


async def get_payments_from_db(user_id: str) -> List[aiosqlite.Row]:
    """
    Получает все платежи пользователя из базы данных.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM payments WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchall()


async def get_all_payments_from_db() -> List[aiosqlite.Row]:
    """
    Получает все платежи из базы данных.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM payments') as cursor:
            return await cursor.fetchall()


async def get_user_from_db(user_id: str) -> Optional[aiosqlite.Row]:
    """
    Получает информацию о пользователе из базы данных по user_id.
    Возвращает строку с данными пользователя или None, если пользователь не найден.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()


async def get_all_users() -> List[str]:
    """
    Получает список всех пользователей из базы данных.
    Возвращает список user_id всех пользователей.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT user_id FROM users') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


async def verify_referral(referral_user_id: str, use: bool = False) -> Union[bool, Tuple[bool, Optional[int]]]:
    """
    Проверяет, существует ли запись о реферале в базе данных.
    use параметр определяет используется ли бонус реферала.
    Если use=True, то помечает бонус как использованный и возвращает user_id реферера.
    Если use=False, то просто проверяет был ли юзер рефералом и возвращает True/False.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT referrer_user_id, used FROM referrals WHERE referral_user_id = ?', (referral_user_id,)) as cursor:
            result = await cursor.fetchone()
            if use:
                if not result:
                    return False, None
                referrer_user_id, used = result
                if used != 1:
                    await db.execute('UPDATE referrals SET used = 1 WHERE referral_user_id = ?', (referral_user_id,))
                    await db.commit()
                    return True, referrer_user_id
                return False, None
            else:
                return bool(result)


async def add_referral_to_db(referrer_user_id: str, referral_user_id: str) -> None:
    """
    Добавляет запись о реферале в базу данных.
    Если запись уже существует, то ничего не делает.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                'INSERT INTO referrals (referrer_user_id, referral_user_id) VALUES (?, ?)',
                (referrer_user_id, referral_user_id)
            )
            await db.commit()
        except aiosqlite.IntegrityError:
            # Игнорируем, если запись уже существует
            pass
