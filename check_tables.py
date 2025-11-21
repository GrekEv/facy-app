#!/usr/bin/env python3
"""РСРѕРІРµСРєР° С‚Р°РР»РС† РїСРѕРµРєС‚Р° РІ РР°Р·Рµ РґР°РЅРЅСС"""
import asyncio
from database.database import get_engine
from sqlalchemy import text

async def check_tables():
    engine = get_engine()
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('users', 'generations', 'transactions', 'promo_codes', 'payment_methods', 'withdrawals', 'reports', 'audit_logs', 'rate_limits')
            ORDER BY table_name
        """))
        tables = [r[0] for r in result.fetchall()]
        
        print(' РўР°РР»РС†С РїСРѕРµРєС‚Р°:')
        if tables:
            for t in tables:
                print(f'    {t}')
        else:
            print('     РўР°РР»РС†С РїСРѕРµРєС‚Р° РµСРµ РЅРµ СРѕР·РґР°РЅС')
            print('    РћРЅР РСѓРґСѓС‚ СРѕР·РґР°РЅС Р°РІС‚РѕРјР°С‚РС‡РµСРєР РїСР РїРµСРІРѕРј РСРїРѕР»СР·РѕРІР°РЅРР')

if __name__ == "__main__":
    asyncio.run(check_tables())

