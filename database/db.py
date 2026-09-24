"""
database/db.py
---------------
طبقة قاعدة البيانات (SQLite) باستخدام aiosqlite (Async بالكامل).

الجداول:
- users: لتخزين المستخدمين الذين بدأوا استخدام البوت (مفيد لاحقًا
  عند إضافة ميزات مثل الإشعارات أو الرسائل الجماعية).
- exchange_rates_history: سجل تاريخي بكل تحديث تم نشره، مفيد لاحقًا
  عند إضافة رسوم بيانية أو تنبيهات أسعار.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import aiosqlite

logger = logging.getLogger(__name__)

DB_PATH = "database/bot_data.db"


async def init_db() -> None:
    """ينشئ الجداول إن لم تكن موجودة بالفعل."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                joined_at TEXT NOT NULL
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS exchange_rates_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usd_try REAL NOT NULL,
                eur_try REAL NOT NULL,
                syp_try_1000 REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        await db.commit()
    logger.info("تم تهيئة قاعدة البيانات بنجاح.")


async def save_user(user_id: int, username: Optional[str]) -> None:
    """يحفظ مستخدمًا جديدًا (أو يتجاهله إن كان محفوظًا مسبقًا)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, joined_at) VALUES (?, ?, ?)",
            (user_id, username, datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()


async def save_rates_history(usd: float, eur: float, syp: float) -> None:
    """يحفظ سجلاً جديدًا في كل مرة يتم فيها نشر تحديث تلقائي."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO exchange_rates_history (usd_try, eur_try, syp_try_1000, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (usd, eur, syp, datetime.now(timezone.utc).isoformat()),
        )
        await db.commit()
