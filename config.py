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

