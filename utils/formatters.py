"""
utils/formatters.py
--------------------
جميع دوال تنسيق الرسائل النصية في مكان واحد لتجنب تكرار الكود
بين المعالجات (handlers) والمجدول (scheduler).
"""

from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("Europe/Istanbul")


def get_timestamp() -> str:
    """يعيد التاريخ والوقت الحالي بتوقيت تركيا بصيغة مقروءة."""
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M")


def format_welcome_message() -> str:
    return (
        "👋 <b>أهلاً بك في بوت أسعار الصرف!</b>\n\n"
        "🇹🇷 تابع أسعار صرف الدولار الأمريكي واليورو والليرة السورية "
        "مقابل الليرة التركية لحظة بلحظة.\n\n"
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


def format_all_message(rates: dict) -> str:
    return (
        "💱 <b>أسعار الصرف</b>\n\n"
        "🇺🇸 <b>الدولار الأمريكي</b>\n"
        f"1 USD = <b>{rates['USD']:.2f}</b> TRY\n\n"
        "🇪🇺 <b>اليورو</b>\n"
        f"1 EUR = <b>{rates['EUR']:.2f}</b> TRY\n\n"
        "🇸🇾 <b>الليرة السورية</b>\n"
        f"1000 SYP = <b>{rates['SYP']:.2f}</b> TRY\n\n"
        f"🕒 آخر تحديث: {get_timestamp()}"
    )


def format_error_message() -> str:
    return "⚠️ حدث خطأ أثناء جلب السعر حاليًا، يرجى المحاولة لاحقًا."
