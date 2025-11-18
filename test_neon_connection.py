#!/usr/bin/env python3
"""Скрипт для проверки подключения к Neon PostgreSQL"""
import asyncio
import sys
from database.database import get_engine
from sqlalchemy import text
from config import settings

async def test_connection():
    """Проверить подключение к базе данных"""
    print("🔍 Проверка подключения к Neon PostgreSQL...")
    print(f"📋 DATABASE_URL: {settings.DATABASE_URL[:50]}..." if settings.DATABASE_URL else "❌ DATABASE_URL не установлен")
    print()
    
    if not settings.DATABASE_URL:
        print("❌ Ошибка: DATABASE_URL не установлен!")
        print("💡 Установите переменную окружения DATABASE_URL")
        print("   Пример: export DATABASE_URL='postgresql+asyncpg://user:pass@host/db'")
        return False
    
    if not settings.DATABASE_URL.startswith("postgresql"):
        print(f"⚠️  Предупреждение: DATABASE_URL не является PostgreSQL URL")
        print(f"   Текущий формат: {settings.DATABASE_URL.split('://')[0] if '://' in settings.DATABASE_URL else 'unknown'}")
        print()
    
    try:
        print("🔄 Подключение к базе данных...")
        engine = get_engine()
        
        async with engine.connect() as conn:
            # Проверка версии PostgreSQL
            print("📊 Проверка версии PostgreSQL...")
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Версия PostgreSQL: {version.split(',')[0]}")
            
            # Проверка текущей базы данных
            print("📊 Проверка текущей базы данных...")
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"✅ Текущая БД: {db_name}")
            
            # Проверка текущего пользователя
            print("📊 Проверка текущего пользователя...")
            result = await conn.execute(text("SELECT current_user"))
            user = result.scalar()
            print(f"✅ Текущий пользователь: {user}")
            
            # Проверка таблиц
            print("📊 Проверка существующих таблиц...")
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            if tables:
                print(f"✅ Найдено таблиц: {len(tables)}")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("⚠️  Таблицы не найдены (это нормально для нового проекта)")
            
            print()
            print("🎉 Подключение к Neon успешно установлено!")
            return True
            
    except ValueError as e:
        print(f"❌ Ошибка инициализации: {e}")
        print("💡 Проверьте, что DATABASE_URL установлен правильно")
        return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        print()
        print("💡 Возможные причины:")
        print("   1. Неправильный формат DATABASE_URL")
        print("   2. Неверные учетные данные")
        print("   3. База данных недоступна")
        print("   4. Проблемы с сетью")
        print()
        print("📚 Проверьте инструкцию в NEON_SETUP.md")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)

