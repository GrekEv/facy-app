# -*- coding: utf-8 -*-
"""Запуск FastAPI сервера"""
import uvicorn
import asyncio
import os
from config import settings
from database import init_db


async def startup():
    """Инициализация при запуске"""
    await init_db()
    port = settings.port
    print(f" Database initialized")
    print(f" API server starting on http://{settings.HOST}:{port}")
    print(f" Web App available at {settings.webapp_url}")


if __name__ == "__main__":
    # Инициализируем БД
    asyncio.run(startup())
    
    # Определяем режим (dev/prod)
    is_dev = os.getenv("ENVIRONMENT", "production") == "development"
    port = settings.port
    
    # Запускаем сервер
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=port,
        reload=is_dev,
        log_level="info"
    )
