"""Конфигурация приложения"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram
    BOT_TOKEN: str
    WEBAPP_URL: str
    
    # API Keys
    DEEPFACE_API_KEY: str = ""
    DEEPFACE_API_URL: str = "https://deepfacevideo.com/api"
    
    FFANS_API_KEY: str = ""
    FFANS_API_URL: str = "https://ffans.ai/api"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    @property
    def port(self) -> int:
        """Получить порт из переменной окружения PORT (для Railway)"""
        import os
        return int(os.getenv("PORT", self.PORT))
    
    # Admin
    ADMIN_IDS: str = ""
    
    # Payment providers
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    YOOKASSA_SHOP_ID: str = ""
    YOOKASSA_SECRET_KEY: str = ""
    
    # Crypto payments
    CRYPTO_API_KEY: str = ""  # Для блокчейн API (например, BlockCypher, Blockchain.info)
    CRYPTO_WALLET_ADDRESS_BTC: str = ""
    CRYPTO_WALLET_ADDRESS_ETH: str = ""
    CRYPTO_WALLET_ADDRESS_USDT: str = ""
    
    # Payment settings
    MIN_WITHDRAWAL: float = 100.0  # Минимальная сумма вывода
    WITHDRAWAL_FEE_PERCENT: float = 5.0  # Комиссия на вывод (%)
    REFERRAL_COMMISSION_PERCENT: float = 50.0  # Комиссия реферальной программы (%)
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Получить список ID администраторов"""
        if not self.ADMIN_IDS:
            return []
        return [int(id.strip()) for id in self.ADMIN_IDS.split(",") if id.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

