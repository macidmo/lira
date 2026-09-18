"""
services/exchange_service.py
-----------------------------
كل الدوال الخاصة بجلب أسعار الصرف من ExchangeRate-API موجودة هنا فقط،
حتى لا يتكرر أي كود متعلق بالاتصال بالـ API في أي مكان آخر من المشروع.

يستخدم الإصدار v6 من ExchangeRate-API عبر خاصية Pair Conversion:
https://v6.exchangerate-api.com/v6/API_KEY/pair/BASE/TARGET
"""

import logging
from typing import Dict

import aiohttp

from config import config

logger = logging.getLogger(__name__)


class ExchangeAPIError(Exception):
    """يُرفع عند فشل جلب البيانات من ExchangeRate-API."""


class ExchangeService:
    """
    خدمة مسؤولة فقط عن التواصل مع ExchangeRate-API وجلب أسعار الصرف.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = config.EXCHANGE_API_BASE_URL

    async def _get_pair_rate(self, base: str, target: str) -> float:
        """
        يجلب سعر الصرف بين عملتين عبر Pair Conversion Endpoint.
        يرفع ExchangeAPIError في حال فشل الطلب أو رد الـ API بخطأ.
        """
        url = f"{self.base_url}/{self.api_key}/pair/{base}/{target}"

        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    data = await response.json()
        except Exception as exc:  # مشاكل الشبكة، Timeout، إلخ
            logger.error("فشل الاتصال بـ ExchangeRate-API (%s -> %s): %s", base, target, exc)
            raise ExchangeAPIError(str(exc)) from exc

        if data.get("result") != "success":
            error_type = data.get("error-type", "unknown_error")
            logger.error("خطأ من ExchangeRate-API (%s -> %s): %s", base, target, error_type)
            raise ExchangeAPIError(error_type)

        return float(data["conversion_rate"])

    async def get_usd_try(self) -> float:
        """1 USD بالليرة التركية."""
        return await self._get_pair_rate("USD", "TRY")

    async def get_eur_try(self) -> float:
        """1 EUR بالليرة التركية."""
        return await self._get_pair_rate("EUR", "TRY")

    async def get_syp_try_per_1000(self) -> float:
        """1000 SYP بالليرة التركية."""
        rate = await self._get_pair_rate("SYP", "TRY")
        return rate * 1000

    async def get_all_rates(self) -> Dict[str, float]:
        """
        يجلب جميع الأسعار المطلوبة (USD, EUR, SYP) دفعة واحدة.
        """
        usd = await self.get_usd_try()
        eur = await self.get_eur_try()
        syp = await self.get_syp_try_per_1000()
        return {"USD": usd, "EUR": eur, "SYP": syp}
