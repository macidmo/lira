import logging
from typing import Any, Callable, Dict, Awaitable, List
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

from config import config

logger = logging.getLogger(__name__)


def build_subscription_keyboard(channels: List[str]) -> InlineKeyboardMarkup:
    """بناء لوحة الأزرار الشفافة للقنوات مع زر التحقق"""
    buttons = []
    for ch in channels:
        clean_username = ch.replace("@", "")
        buttons.append([
            InlineKeyboardButton(
                text=f"📢 {clean_username}",
                url=f"https://t.me/{clean_username}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="🔄 تحقق من الاشتراك",
            callback_data="check_subscription"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


class RequiredSubscriptionMiddleware(BaseMiddleware):
    """Middleware للتحقق من اشتراك المستخدم الإجباري بالقنوات"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        channels = config.get_required_channels()
        if not channels:
            return await handler(event, data)

        bot: Bot = data.get("bot")
        user = data.get("event_from_user")

        if not user or user.is_bot:
            return await handler(event, data)

        # التحقق مما إذا كان المستخدم ضغط على زر "تحقق من الاشتراك"
        is_check_callback = False
        if isinstance(event, CallbackQuery) and event.data == "check_subscription":
            is_check_callback = True

        unsubscribed_channels = []

        for channel in channels:
            try:
                member = await bot.get_chat_member(chat_id=channel, user_id=user.id)
                if member.status in ["creator", "administrator"]:
                    # استثناء المالك والمشرفين تلقائياً
                    continue
                if member.status not in ["member"]:
                    unsubscribed_channels.append(channel)
            except TelegramBadRequest as e:
                logger.error(f"فشل التحقق من قناة {channel}: {e}")
                # في حال تعذر الوصول للقناة أو كانت خطأ لا نمنع المستخدم
                continue

        # إذا كان مشتركاً في جميع القنوات المطلوب الاشتراكات فيها
        if not unsubscribed_channels:
            if is_check_callback and isinstance(event, CallbackQuery):
                await event.answer("✅ شكراً لك! تم التأكد من اشتراكك بنجاح.", show_alert=True)
                try:
                    await event.message.delete()
                except Exception:
                    pass
            return await handler(event, data)

        # إذا لم يكن مشتركاً
        text = "⚠️ <b>يجب الاشتراك في القنوات التالية أولاً لاستخدام البوت:</b>\n\nبعد الاشتراك اضغط على: <b>تحقق من الاشتراك</b>"
        reply_markup = build_subscription_keyboard(unsubscribed_channels)

        if isinstance(event, Message):
            await event.answer(text, reply_markup=reply_markup)
            return None

        elif isinstance(event, CallbackQuery):
            if is_check_callback:
                await event.answer("❌ لم تقم بالاشتراك في جميع القنوات بعد!", show_alert=True)
            else:
                await event.answer("⚠️ يجب عليك الاشتراك بالقنوات أولاً!", show_alert=True)
                try:
                    await event.message.edit_text(text, reply_markup=reply_markup)
                except Exception:
                    pass
            return None

        return await handler(event, data)