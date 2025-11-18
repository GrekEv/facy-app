"""
Vercel Serverless Function для FastAPI приложения
Этот файл адаптирует FastAPI для работы на Vercel
"""
import sys
import os
import logging
from pathlib import Path
from mangum import Mangum

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Добавляем корневую директорию в путь
    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(BASE_DIR))
    
    # Убеждаемся, что DATABASE_URL настроен (для serverless нужен PostgreSQL)
    if not os.getenv("DATABASE_URL"):
        logger.warning("DATABASE_URL not set. Using default PostgreSQL connection string.")
        # Можно установить дефолтное значение или выбросить ошибку
        # os.environ["DATABASE_URL"] = "postgresql+asyncpg://..."
    
    # Импортируем приложение FastAPI
    from api.main import app
    
    # Mangum адаптирует ASGI приложение (FastAPI) для AWS Lambda/Vercel
    handler = Mangum(app, lifespan="off")
    
    logger.info("FastAPI app initialized successfully")
    
except Exception as e:
    logger.error(f"Error initializing FastAPI app: {e}", exc_info=True)
    # Создаем минимальный handler для обработки ошибок
    from fastapi import FastAPI
    error_app = FastAPI()
    
    @error_app.get("/{path:path}")
    @error_app.post("/{path:path}")
    async def error_handler(path: str):
        return {
            "error": "Application initialization failed",
            "details": str(e),
            "path": path
        }
    
    handler = Mangum(error_app, lifespan="off")
    app = error_app  # Для локального тестирования

# Для локального тестирования
if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=3000)
    except NameError:
        logger.error("App not initialized, cannot run locally")

