#!/usr/bin/env python3
"""��о�та� п�ове�ка подкл�чен�� к �азе данн��"""
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
                print(f" �одкл�чен�е у�пешно!")
                print(f"PostgreSQL: {row[0]}")
                print(f"База данн��: {row[1]}")
                print(f"�ол�зовател�: {row[2]}")
                
                # ��ове�ка та�л�ц
                result = await conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                count = result.fetchone()[0]
                print(f"Та�л�ц в �азе: {count}")
                return True
    except Exception as e:
        print(f" Ош��ка: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(check())
    sys.exit(0 if success else 1)

