"""
handlers/currency.py
---------------------
معالجات أزرار الأسعار (الدولار / اليورو / الليرة السورية / جميع الأسعار)
عند الضغط على أي زر من لوحة المفاتيح الرئيسية.
"""

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from config import config
from keyboards.inline import back_to_menu_keyboard, main_menu_keyboard
from services.exchange_service import ExchangeAPIError, ExchangeService
from utils.formatters import (
    format_all_message,
    format_error_message,
    format_eur_message,
    format_syp_message,
    format_usd_message,
    format_welcome_message,
)

logger = logging.getLogger(__name__)
router = Router(name="currency")

exchange_service = ExchangeService(config.API_KEY)


@router.callback_query(F.data == "rate_usd")
async def show_usd(callback: CallbackQuery) -> None:
    await _handle_rate_request(callback, "usd")


@router.callback_query(F.data == "rate_eur")
async def show_eur(callback: CallbackQuery) -> None:
    await _handle_rate_request(callback, "eur")


@router.callback_query(F.data == "rate_syp")
async def show_syp(callback: CallbackQuery) -> None:
    await _handle_rate_request(callback, "syp")


@router.callback_query(F.data == "rate_all")
async def show_all(callback: CallbackQuery) -> None:
    await _handle_rate_request(callback, "all")


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        format_welcome_message(),
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


async def _handle_rate_request(callback: CallbackQuery, kind: str) -> None:
    """
    دالة موحّدة لجلب وعرض السعر المطلوب، لتفادي تكرار نفس منطق
    الجلب والمعالجة والأخطاء في كل معالج على حدة.
    """
    await callback.answer("⏳ جاري جلب السعر...")

    try:
        if kind == "usd":
            rate = await exchange_service.get_usd_try()
            text = format_usd_message(rate)
        elif kind == "eur":
            rate = await exchange_service.get_eur_try()
            text = format_eur_message(rate)
        elif kind == "syp":
            rate = await exchange_service.get_try_syp_per_1000()
            text = format_syp_message(rate)
        else:
            rates = await exchange_service.get_all_rates()
            text = format_all_message(rates)

        await callback.message.edit_text(text, reply_markup=back_to_menu_keyboard())

    except ExchangeAPIError:
        logger.exception("فشل جلب السعر (%s) من ExchangeRate-API.", kind)
        await callback.message.edit_text(
            format_error_message(), reply_markup=back_to_menu_keyboard()
        )
    except Exception:
        logger.exception("خطأ غير متوقع أثناء معالجة طلب السعر (%s).", kind)
        await callback.message.edit_text(
            format_error_message(), reply_markup=back_to_menu_keyboard()
        )
