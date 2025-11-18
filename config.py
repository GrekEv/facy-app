from pydantic_settings import BaseSettings
from typing import List
class Settings(BaseSettings):
    BOT_TOKEN: str
    WEBAPP_URL: str = ""
    @property
    def webapp_url(self) -> str:
        import os
        if self.WEBAPP_URL:
            return self.WEBAPP_URL
        railway_url = os.getenv("RAILWAY_PUBLIC_DOMAIN")
        if railway_url:
            return f"https://{railway_url}"
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        if render_url:
            return render_url
        port = self.port
        return f"http://{self.HOST}:{port}"
    ENVIRONMENT: str = "production"
    DEEPFACE_API_KEY: str = ""
    DEEPFACE_API_URL: str = "https://deepfacevideo.com/api"
    FACESWAP_API_KEY: str = ""
    FACESWAP_API_URL: str = "https://faceswap.ru/api"
    DEEPSWAP_API_KEY: str = ""
    DEEPSWAP_API_URL: str = "https://api.deepswap.ai"
    FFANS_API_KEY: str = ""
    FFANS_API_URL: str = "https://ffans.ai/api"
    OPENAI_API_KEY: str = ""
    SORA_MODEL: str = "sora"
    PROXY_URL: str = ""
    RUNWAY_API_KEY: str = ""
    RUNWAY_API_URL: str = "https://api.runwayml.com/v1"
    PIKA_API_KEY: str = ""
    PIKA_API_URL: str = "https://api.pika.art/v1"
    REPLICATE_API_KEY: str = ""
    REPLICATE_API_URL: str = "https://api.replicate.com/v1"
    HIGGSFIELD_API_KEY: str = ""
    HIGGSFIELD_API_URL: str = "https://api.higgsfield.ai"
    LEONARDO_API_KEY: str = ""
    LEONARDO_API_URL: str = "https://cloud.leonardo.ai/api/rest/v1"
    VIDEO_GENERATION_PROVIDER: str = "replicate"
    IMAGE_GENERATION_PROVIDER: str = "replicate"
    REPLICATE_IMAGE_MODEL: str = "ideogram-ai/ideogram-v3-turbo"
    REPLICATE_VIDEO_MODEL: str = "minimax/video-01"
    DATABASE_URL: str = ""
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    @property
    def port(self) -> int:
        import os
        return int(os.getenv("PORT", self.PORT))
    ADMIN_IDS: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    YOOKASSA_SHOP_ID: str = ""
    YOOKASSA_SECRET_KEY: str = ""
    CRYPTO_API_KEY: str = ""
    CRYPTO_WALLET_ADDRESS_BTC: str = ""
    CRYPTO_WALLET_ADDRESS_ETH: str = ""
    CRYPTO_WALLET_ADDRESS_USDT: str = ""
    MIN_WITHDRAWAL: float = 100.0
    WITHDRAWAL_FEE_PERCENT: float = 5.0
    REFERRAL_COMMISSION_PERCENT: float = 50.0
    STANDARD_PLAN_PAYMENT_URL: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "OnlyFace"
    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(id.strip()) for id in self.ADMIN_IDS.split(",") if id.strip()]
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"
settings = Settings()
