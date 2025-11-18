#!/usr/bin/env python3
"""��ове�ка та�л�ц п�оекта в �азе данн��"""
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
        
        print(' Та�л�ц� п�оекта:')
        if tables:
            for t in tables:
                print(f'    {t}')
        else:
            print('     Та�л�ц� п�оекта е�е не �оздан�')
            print('    Он� �удут �оздан� автомат�че�к� п�� пе�вом ��пол�зован��')

if __name__ == "__main__":
    asyncio.run(check_tables())

