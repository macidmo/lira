import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    API_KEY: str = os.getenv("API_KEY", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    REQUIRED_CHANNELS: str = os.getenv("REQUIRED_CHANNELS", "")

    # --- إعدادات الذهب (Hasfiyat API) ---
    HASFIYAT_API_KEY: str = os.getenv("HASFIYAT_API_KEY", "")
    GOLD_SOURCE: str = os.getenv("GOLD_SOURCE", "harem")
    GOLD_SYMBOL: str = os.getenv("GOLD_SYMBOL", "GRAM ALTIN")

    EXCHANGE_API_BASE_URL: str = "https://v6.exchangerate-api.com/v6"
    HASFIYAT_BASE_URL: str = "https://api.hasfiyat.com"

    def get_required_channels(self) -> List[str]:
        """تحويل سلسلة القنوات المفصولة بفواصل إلى قائمة نظيفة"""
        if not self.REQUIRED_CHANNELS.strip():
            return []
        return [ch.strip() for ch in self.REQUIRED_CHANNELS.split(",") if ch.strip()]

    def validate(self) -> None:
        missing = [
            name
            for name, value in [
                ("BOT_TOKEN", self.BOT_TOKEN),
                ("API_KEY", self.API_KEY),
                ("CHANNEL_ID", self.CHANNEL_ID),
                ("HASFIYAT_API_KEY", self.HASFIYAT_API_KEY),
            ]
            if not value
        ]
        if missing:
            raise ValueError(
                "❌ المتغيرات التالية مفقودة في ملف .env: " + ", ".join(missing)
            )


config = Config()