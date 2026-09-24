import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.db import init_db
from handlers import currency, start
from middlewares.subscription import RequiredSubscriptionMiddleware
from scheduler.scheduler import RateBroadcaster
from utils.logger import setup_logger

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logger()
    config.validate()

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # تسجيل Middleware الاشتراك الإجباري
    subscription_middleware = RequiredSubscriptionMiddleware()
    dp.message.outer_middleware(subscription_middleware)
    dp.callback_query.outer_middleware(subscription_middleware)

    # تسجيل جميع المعالجات (Routers)
    dp.include_router(start.router)
    dp.include_router(currency.router)

    # تهيئة قاعدة البيانات
    await init_db()

    # تشغيل المجدول (النشر التلقائي كل ساعة)
    broadcaster = RateBroadcaster(bot)
    broadcaster.start()

    logger.info("✅ تم تشغيل البوت بنجاح.")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.getLogger(__name__).info("تم إيقاف البوت يدويًا.")