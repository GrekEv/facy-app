"""Запу�к FastAPI �е�ве�а"""
import uvicorn
import asyncio
import os
from config import settings
from database import init_db


async def startup():
    """Ин�ц�ал�зац�� п�� запу�ке"""
    await init_db()
    port = settings.port
    print(f" Database initialized")
    print(f" API server starting on http://{settings.HOST}:{port}")
    print(f" Web App available at {settings.webapp_url}")


if __name__ == "__main__":
    # Ин�ц�ал�з��уем Б�
    asyncio.run(startup())
    
    # Оп�едел�ем �еж�м (dev/prod)
    is_dev = os.getenv("ENVIRONMENT", "production") == "development"
    port = settings.port
    
    # Запу�каем �е�ве�
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=port,
        reload=is_dev,
        log_level="info"
    )

