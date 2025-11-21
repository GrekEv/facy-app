#!/usr/bin/env python3
"""РСРѕСС‚Р°С РїСРѕРІРµСРєР° РїРѕРґРєР»СС‡РµРЅРС Рє РР°Р·Рµ РґР°РЅРЅСС"""
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
                print(f" РРѕРґРєР»СС‡РµРЅРРµ СѓСРїРµС€РЅРѕ!")
                print(f"PostgreSQL: {row[0]}")
                print(f"Р‘Р°Р·Р° РґР°РЅРЅСС: {row[1]}")
                print(f"РРѕР»СР·РѕРІР°С‚РµР»С: {row[2]}")
                
                # РСРѕРІРµСРєР° С‚Р°РР»РС†
                result = await conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                count = result.fetchone()[0]
                print(f"РўР°РР»РС† РІ РР°Р·Рµ: {count}")
                return True
    except Exception as e:
        print(f" РћС€РРРєР°: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(check())
    sys.exit(0 if success else 1)

