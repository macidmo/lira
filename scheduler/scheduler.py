"""
scheduler/scheduler.py
------------------------
ينشر تحديث أسعار الصرف تلقائيًا داخل قناة تيليجرام كل ساعة تمامًا،
بغض النظر عن تغيّر السعر من عدمه.
"""

import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import config
from database.db import save_rates_history
from services.exchange_service import ExchangeAPIError, ExchangeService
from utils.formatters import format_all_message

logger = logging.getLogger(__name__)


class RateBroadcaster:
    """يدير مهمة النشر التلقائي كل ساعة داخل القناة."""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.exchange_service = ExchangeService(config.API_KEY)
        self.scheduler = AsyncIOScheduler(timezone="Europe/Istanbul")

    def start(self) -> None:
        self.scheduler.add_job(
            self.broadcast_rates,
            trigger=CronTrigger(minute=0),  # كل ساعة تمامًا (عند الدقيقة 0)
            id="hourly_rate_broadcast",
            replace_existing=True,
            misfire_grace_time=120,
        )
        self.scheduler.start()
        logger.info("تم تشغيل المجدول بنجاح، سيتم النشر كل ساعة تمامًا.")

    async def broadcast_rates(self) -> None:
        """
        يجلب الأسعار وينشرها في القناة. عند فشل الاتصال بالـ API،
        يسجل الخطأ فقط ولا يوقف البوت، وتُعاد المحاولة عند التحديث القادم.
        """
        try:
            rates = await self.exchange_service.get_all_rates()
        except ExchangeAPIError:
            logger.exception(
                "فشل جلب الأسعار للنشر التلقائي، ستُعاد المحاولة عند التحديث القادم."
            )
            return
        except Exception:
            logger.exception("خطأ غير متوقع أثناء جلب الأسعار للنشر التلقائي.")
            return

        try:
            await self.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=format_all_message(rates),
            )
            await save_rates_history(rates["USD"], rates["EUR"], rates["SYP"])
            logger.info("تم نشر تحديث الأسعار في القناة بنجاح.")
        except Exception:
            logger.exception("فشل نشر الرسالة داخل القناة. تحقق من صلاحيات البوت.")
