"""Работа с базой данных"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from .models import Base
from config import settings
import os


# Создаем движок базы данных
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Инициализация базы данных"""
    # Создаем директорию для БД если не существует
    db_dir = os.path.dirname(settings.DATABASE_URL.replace("sqlite+aiosqlite:///", ""))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Получить сессию базы данных"""
    async with AsyncSessionLocal() as session:
        yield session

