"""Конфигурация приложения"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram
    BOT_TOKEN: str
    WEBAPP_URL: str = ""  # Опционально - можно использовать домен или Railway/Render/ngrok URL
    
    @property
    def webapp_url(self) -> str:
        """Получить URL Web App с автоматическим определением"""
        import os
        
        # Если указан явно, используем его
        if self.WEBAPP_URL:
            return self.WEBAPP_URL
        
        # Пытаемся определить автоматически из переменных окружения
        # Railway, Render и другие платформы часто предоставляют URL
        railway_url = os.getenv("RAILWAY_PUBLIC_DOMAIN")
        if railway_url:
            return f"https://{railway_url}"
        
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        if render_url:
            return render_url
        
        # Если ничего не найдено, используем локальный хост
        port = self.port
        return f"http://{self.HOST}:{port}"
    
    # Environment
    ENVIRONMENT: str = "production"  # development, production
    
    # API Keys для замены лиц
    DEEPFACE_API_KEY: str = ""
    DEEPFACE_API_URL: str = "https://deepfacevideo.com/api"
    
    # Альтернативные сервисы для замены лиц
    FACESWAP_API_KEY: str = ""
    FACESWAP_API_URL: str = "https://faceswap.ru/api"
    DEEPSWAP_API_KEY: str = ""
    DEEPSWAP_API_URL: str = "https://api.deepswap.ai"
    
    # API Keys для генерации изображений
    FFANS_API_KEY: str = ""
    FFANS_API_URL: str = "https://ffans.ai/api"
    
    # API Keys для генерации видео
    # OpenAI Sora (когда будет доступен)
    OPENAI_API_KEY: str = ""
    SORA_MODEL: str = "sora"  # Модель Sora
    
    # RunwayML
    RUNWAY_API_KEY: str = ""
    RUNWAY_API_URL: str = "https://api.runwayml.com/v1"
    
    # Pika Labs
    PIKA_API_KEY: str = ""
    PIKA_API_URL: str = "https://api.pika.art/v1"
    
    # Stable Video Diffusion (через Replicate или другие провайдеры)
    REPLICATE_API_KEY: str = ""
    REPLICATE_API_URL: str = "https://api.replicate.com/v1"
    
    # Higgsfield.ai (для генерации видео)
    HIGGSFIELD_API_KEY: str = ""
    HIGGSFIELD_API_URL: str = "https://api.higgsfield.ai"
    
    # Leonardo.AI (для изображений и видео)
    LEONARDO_API_KEY: str = ""
    LEONARDO_API_URL: str = "https://cloud.leonardo.ai/api/rest/v1"
    
    # Выбор провайдера по умолчанию
    VIDEO_GENERATION_PROVIDER: str = "sora"  # sora, ffans, runway, pika, replicate, higgsfield, leonardo
    IMAGE_GENERATION_PROVIDER: str = "openai"  # openai, ffans, leonardo, replicate
    
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
        extra = "ignore"  # Игнорировать дополнительные поля из .env


settings = Settings()

