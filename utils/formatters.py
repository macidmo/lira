"""
utils/formatters.py
--------------------
جميع دوال تنسيق الرسائل النصية في مكان واحد لتجنب تكرار الكود
بين المعالجات (handlers) والمجدول (scheduler).
"""

from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from services.gold_service import GoldPrices

TIMEZONE = ZoneInfo("Europe/Istanbul")


def get_timestamp() -> str:
    """يعيد التاريخ والوقت الحالي بتوقيت تركيا بصيغة مقروءة."""
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M")


def format_welcome_message() -> str:
    return (
        "👋 <b>أهلاً بك في بوت أسعار الصرف!</b>\n\n"
        "🇹🇷 تابع أسعار صرف الدولار الأمريكي واليورو والليرة السورية "
        "مقابل الليرة التركية، وسعر الذهب (عيار 24 و21) لحظة بلحظة.\n\n"
        "اختر أحد الخيارات أدناه للاطلاع على السعر 👇"
    )


def format_usd_message(rate: float) -> str:
    return (
        "💵 <b>الدولار الأمريكي</b>\n\n"
        f"1 USD = <b>{rate:.2f}</b> TRY\n\n"
        f"🕒 آخر تحديث: {get_timestamp()}"
    )


def format_eur_message(rate: float) -> str:
    return (
        "💶 <b>اليورو</b>\n\n"
        f"1 EUR = <b>{rate:.2f}</b> TRY\n\n"
        f"🕒 آخر تحديث: {get_timestamp()}"
    )


def format_syp_message(rate_per_1000: float) -> str:
    return (
        "🇸🇾 <b>الليرة السورية</b>\n\n"
        f"1000 SYP = <b>{rate_per_1000:.2f}</b> TRY\n\n"
        f"🕒 آخر تحديث: {get_timestamp()}"
    )


def _gold_block(gold: GoldPrices) -> str:
    """كتلة نص الذهب (تُستخدم في رسالة الذهب وفي رسالة جميع الأسعار)."""
    return (
        "🔸 <b>عيار 24</b>\n"
        f"بيع: <b>{gold.sell_24:,.2f}</b> TRY\n"
        f"شراء: <b>{gold.buy_24:,.2f}</b> TRY\n\n"
        "🔸 <b>عيار 21</b>\n"
        f"بيع: <b>{gold.sell_21:,.2f}</b> TRY\n"
        f"شراء: <b>{gold.buy_21:,.2f}</b> TRY"
    )


def format_gold_message(gold: GoldPrices) -> str:
    return (
        "🥇 <b>الذهب</b> — سعر الغرام بالليرة التركية\n\n"
        f"{_gold_block(gold)}\n\n"
        "ℹ️ عيار 21 محسوب من عيار 24 (× 21 ÷ 24) بدون مصنعية.\n\n"
        f"🕒 آخر تحديث: {get_timestamp()}"
    )


def format_all_message(rates: dict, gold: Optional[GoldPrices] = None) -> str:
    text = (
        "💱 <b>أسعار الصرف</b>\n\n"
        "🇺🇸 <b>الدولار الأمريكي</b>\n"
        f"1 USD = <b>{rates['USD']:.2f}</b> TRY\n\n"
        "🇪🇺 <b>اليورو</b>\n"
        f"1 EUR = <b>{rates['EUR']:.2f}</b> TRY\n\n"
        "🇸🇾 <b>الليرة السورية</b>\n"
        f"1000 SYP = <b>{rates['SYP']:.2f}</b> TRY\n\n"
    )
    if gold is not None:
        text += "🥇 <b>الذهب</b> (غرام)\n" + _gold_block(gold) + "\n\n"
    text += f"🕒 آخر تحديث: {get_timestamp()}"
    return text


def format_error_message() -> str:
    return "⚠️ حدث خطأ أثناء جلب السعر حاليًا، يرجى المحاولة لاحقًا."
