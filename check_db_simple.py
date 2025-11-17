#!/usr/bin/env python3
"""Простая проверка подключения к базе данных"""
import asyncio
import sys
from sqlalchemy import text
from database.database import engine

async def check():
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version(), current_database(), current_user"))
            row = result.fetchone()
            if row:
                print(f"✅ Подключение успешно!")
                print(f"PostgreSQL: {row[0]}")
                print(f"База данных: {row[1]}")
                print(f"Пользователь: {row[2]}")
                
                # Проверка таблиц
                result = await conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                count = result.fetchone()[0]
                print(f"Таблиц в базе: {count}")
                return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(check())
    sys.exit(0 if success else 1)

