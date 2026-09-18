"""
keyboards/inline.py
--------------------
جميع لوحات المفاتيح الشفافة (Inline Keyboards) المستخدمة في البوت.
"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """لوحة المفاتيح الرئيسية التي تظهر عند /start."""
    builder = InlineKeyboardBuilder()
    builder.button(text="💵 الدولار", callback_data="rate_usd")
    builder.button(text="💶 اليورو", callback_data="rate_eur")
    builder.button(text="🇸🇾 الليرة السورية", callback_data="rate_syp")
    builder.button(text="💱 جميع الأسعار", callback_data="rate_all")
    builder.adjust(2, 2)
    return builder.as_markup()


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """زر العودة للقائمة الرئيسية، يظهر تحت أي سعر معروض."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 القائمة الرئيسية", callback_data="back_to_menu")
    return builder.as_markup()
