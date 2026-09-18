"""
handlers/start.py
------------------
معالج أمر /start: يرسل رسالة ترحيب مع لوحة مفاتيح شفافة.
"""

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database.db import save_user
from keyboards.inline import main_menu_keyboard
from utils.formatters import format_welcome_message

logger = logging.getLogger(__name__)
router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await save_user(message.from_user.id, message.from_user.username)

    await message.answer(
        format_welcome_message(),
        reply_markup=main_menu_keyboard(),
    )

    logger.info("المستخدم %s بدأ استخدام البوت.", message.from_user.id)
