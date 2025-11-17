"""
Vercel Serverless Function для FastAPI приложения
Этот файл адаптирует FastAPI для работы на Vercel
"""
import sys
from pathlib import Path
from mangum import Mangum

# Добавляем корневую директорию в путь
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Импортируем приложение FastAPI
from api.main import app

# Mangum адаптирует ASGI приложение (FastAPI) для AWS Lambda/Vercel
handler = Mangum(app, lifespan="off")

# Для локального тестирования
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)

