# -*- coding: utf-8 -*-
"""
Yandex Cloud FastAPI Ð´Ð»Ñ FastAPI Ð¿ÑÐÐ»Ð¾Ð¶ÐµÐ½ÐÑ
ÐÑÐ¾Ñ ÑÐ°Ð¹Ð» Ð°Ð´Ð°Ð¿ÑÐÑÑÐµÑ FastAPI Ð´Ð»Ñ ÑÐ°ÐÐ¾ÑÑ Ð½Ð° Yandex Cloud
"""
import sys
import os
import logging
from pathlib import Path
from mangum import Mangum

# ÐÐ°ÑÑÑÐ¾Ð¹ÐºÐ° Ð»Ð¾ÐÐÑÐ¾Ð²Ð°Ð½ÐÑ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # ÐÐ¾ÐÐ°Ð²Ð»ÑÐµÐ¼ ÐºÐ¾ÑÐ½ÐµÐ²ÑÑ Ð´ÐÑÐµÐºÑÐ¾ÑÐÑ Ð² Ð¿ÑÑÑ
    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(BASE_DIR))
    
    # Ð£ÐÐµÐ¶Ð´Ð°ÐµÐ¼ÑÑ, ÑÑÐ¾ DATABASE_URL Ð½Ð°ÑÑÑÐ¾ÐµÐ½ (Ð´Ð»Ñ serverless Ð½ÑÐ¶ÐµÐ½ PostgreSQL)
    if not os.getenv("DATABASE_URL"):
        logger.warning("DATABASE_URL not set. Using default PostgreSQL connection string.")
        # ÐÐ¾Ð¶Ð½Ð¾ ÑÑÑÐ°Ð½Ð¾Ð²ÐÑÑ Ð´ÐµÑÐ¾Ð»ÑÐ½Ð¾Ðµ Ð·Ð½Ð°ÑÐµÐ½ÐÐµ ÐÐ»Ð Ð²ÑÐÑÐ¾ÑÐÑÑ Ð¾ÑÐÐÐºÑ
        # os.environ["DATABASE_URL"] = "postgresql+asyncpg://..."
    
    # ÐÐ¼Ð¿Ð¾ÑÑÐÑÑÐµÐ¼ Ð¿ÑÐÐ»Ð¾Ð¶ÐµÐ½ÐÐµ FastAPI
    from api.main import app
    
    # Mangum Ð°Ð´Ð°Ð¿ÑÐÑÑÐµÑ ASGI Ð¿ÑÐÐ»Ð¾Ð¶ÐµÐ½ÐÐµ (FastAPI) Ð´Ð»Ñ AWS Lambda/Yandex Cloud
    handler = Mangum(app, lifespan="off")
    
    logger.info("FastAPI app initialized successfully")
    
except Exception as e:
    logger.error(f"Error initializing FastAPI app: {e}", exc_info=True)
    # ÐÐ¾Ð·Ð´Ð°ÐµÐ¼ Ð¼ÐÐ½ÐÐ¼Ð°Ð»ÑÐ½ÑÐ¹ handler Ð´Ð»Ñ Ð¾ÐÑÐ°ÐÐ¾ÑÐºÐ Ð¾ÑÐÐÐ¾Ðº
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
    app = error_app  # ÐÐ»Ñ Ð»Ð¾ÐºÐ°Ð»ÑÐ½Ð¾ÐÐ¾ ÑÐµÑÑÐÑÐ¾Ð²Ð°Ð½ÐÑ

# ÐÐ»Ñ Ð»Ð¾ÐºÐ°Ð»ÑÐ½Ð¾ÐÐ¾ ÑÐµÑÑÐÑÐ¾Ð²Ð°Ð½ÐÑ
if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=3000)
    except NameError:
        logger.error("App not initialized, cannot run locally")

