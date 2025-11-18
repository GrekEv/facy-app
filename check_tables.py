#!/usr/bin/env python3
"""Проверка таблиц проекта в базе данных"""
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
        
        print('📊 Таблицы проекта:')
        if tables:
            for t in tables:
                print(f'   ✅ {t}')
        else:
            print('   ⚠️  Таблицы проекта еще не созданы')
            print('   💡 Они будут созданы автоматически при первом использовании')

if __name__ == "__main__":
    asyncio.run(check_tables())

