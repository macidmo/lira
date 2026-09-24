"""
services/gold_service.py
-------------------------
جلب سعر الذهب عيار 24 من Hasfiyat API، وحساب سعر عيار 21 رياضيًا.

المعادلة:
    سعر عيار K = سعر عيار 24 × (K ÷ 24)
    عيار 21 = عيار 24 × 21 ÷ 24 = عيار 24 × 0.875

ملاحظات:
- القيم من الـ API تأتي كنص بالصيغة التركية (مثال: "6.692,74")، لذلك نحوّلها لرقم أولًا.
- buy = ما يشتريه السوق منك، sell = ما يبيعك به السوق (دائمًا buy < sell).
- السعر المحسوب لعيار 21 هو سعر الذهب الخام فقط، بدون مصنعية أو ضريبة.
- يوجد كاش قصير (افتراضيًا 60 ثانية) حتى لا تُستهلك حصة الـ API عند ضغط المستخدمين على الزر.
"""

import logging
import re
import time
from dataclasses import dataclass
from typing import Optional

import aiohttp

from config import config

logger = logging.getLogger(__name__)

KARAT_BASE = 24
TARGET_KARAT = 21


class GoldAPIError(Exception):
    """يُرفع عند فشل جلب سعر الذهب من Hasfiyat API."""


def parse_tr_number(value) -> float:
    """يحوّل رقمًا بالصيغة التركية إلى float. مثال: '6.692,74' -> 6692.74"""
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(" ", "")
    if not text:
        raise ValueError("قيمة سعر فارغة")

    if "," in text:
        # النقطة = فاصل الآلاف، الفاصلة = فاصل عشري
        text = text.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", text):
        # مثال: "6.692" بدون كسور => النقاط هنا فواصل آلاف
        text = text.replace(".", "")

    return float(text)


def karat_price(price_24k: float, karat: int) -> float:
    """يحسب سعر الغرام لعيار معيّن انطلاقًا من سعر عيار 24."""
    return price_24k * karat / KARAT_BASE


@dataclass(frozen=True)
class GoldPrices:
    """سعر غرام الذهب بالليرة التركية (بيع/شراء) لعيار 24 وعيار 21."""

    buy_24: float
    sell_24: float
    buy_21: float
    sell_21: float

    @classmethod
    def from_24k(cls, buy_24: float, sell_24: float) -> "GoldPrices":
        return cls(
            buy_24=buy_24,
            sell_24=sell_24,
            buy_21=karat_price(buy_24, TARGET_KARAT),
            sell_21=karat_price(sell_24, TARGET_KARAT),
        )


class GoldService:
    def __init__(self, cache_ttl: int = 60):
        self.cache_ttl = cache_ttl
        self._cache: Optional[GoldPrices] = None
        self._cache_time: float = 0.0

    async def _fetch_24k(self) -> tuple[float, float]:
        url = f"{config.HASFIYAT_BASE_URL}/api/prices"
        params = {"source": config.GOLD_SOURCE, "symbols": config.GOLD_SYMBOL}
        headers = {"Authorization": f"Bearer {config.HASFIYAT_API_KEY}"}

        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status != 200:
                        body = (await response.text())[:200]
                        raise GoldAPIError(f"HTTP {response.status}: {body}")
                    data = await response.json()
        except GoldAPIError:
            raise
        except Exception as exc:  # شبكة، Timeout، JSON غير صالح...
            logger.error("فشل الاتصال بـ Hasfiyat API: %s", exc)
            raise GoldAPIError(str(exc)) from exc

        items = data.get("data") or []
        if not items:
            raise GoldAPIError(f"لا توجد بيانات للرمز '{config.GOLD_SYMBOL}' في المصدر '{config.GOLD_SOURCE}'")

        if data.get("stale"):
            logger.warning("بيانات الذهب من Hasfiyat قديمة (stale) — المصدر: %s", config.GOLD_SOURCE)

        item = items[0]
        try:
            return parse_tr_number(item["buy"]), parse_tr_number(item["sell"])
        except (KeyError, ValueError) as exc:
            logger.error("صيغة سعر غير متوقعة من Hasfiyat: %s", item)
            raise GoldAPIError(f"صيغة سعر غير متوقعة: {item}") from exc

    async def get_gold_prices(self) -> GoldPrices:
        """يعيد أسعار عيار 24 وعيار 21 (من الكاش إن كان حديثًا)."""
        now = time.monotonic()
        if self._cache is not None and now - self._cache_time < self.cache_ttl:
            return self._cache

        buy_24, sell_24 = await self._fetch_24k()
        prices = GoldPrices.from_24k(buy_24, sell_24)

        self._cache = prices
        self._cache_time = now
        return prices

    async def try_get_gold_prices(self) -> Optional[GoldPrices]:
        """مثل get_gold_prices لكن يعيد None عند الفشل (لا يوقف عرض العملات)."""
        try:
            return await self.get_gold_prices()
        except GoldAPIError:
            logger.exception("تعذّر جلب سعر الذهب، سيتم عرض العملات فقط.")
            return None


# نسخة واحدة مشتركة بين المعالجات والمجدول (لمشاركة الكاش)
gold_service = GoldService()
