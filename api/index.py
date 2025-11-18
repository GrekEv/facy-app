"""
Vercel Serverless Function дл� FastAPI п��ложен��
�тот файл адапт��ует FastAPI дл� �а�от� на Vercel
"""
import sys
import os
import logging
from pathlib import Path
from mangum import Mangum

# �а�т�ойка ло���ован��
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # �о�авл�ем ко�неву� д��екто��� в пут�
    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(BASE_DIR))
    
    # У�еждаем��, что DATABASE_URL на�т�оен (дл� serverless нужен PostgreSQL)
    if not os.getenv("DATABASE_URL"):
        logger.warning("DATABASE_URL not set. Using default PostgreSQL connection string.")
        # �ожно у�танов�т� дефолтное значен�е �л� в���о��т� ош��ку
        # os.environ["DATABASE_URL"] = "postgresql+asyncpg://..."
    
    # Импо�т��уем п��ложен�е FastAPI
    from api.main import app
    
    # Mangum адапт��ует ASGI п��ложен�е (FastAPI) дл� AWS Lambda/Vercel
    handler = Mangum(app, lifespan="off")
    
    logger.info("FastAPI app initialized successfully")
    
except Exception as e:
    logger.error(f"Error initializing FastAPI app: {e}", exc_info=True)
    # �оздаем м�н�мал�н�й handler дл� о��а�отк� ош��ок
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
    app = error_app  # �л� локал�но�о те�т��ован��

# �л� локал�но�о те�т��ован��
if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=3000)
    except NameError:
        logger.error("App not initialized, cannot run locally")

