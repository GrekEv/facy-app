#!/usr/bin/env python3
"""�к��пт дл� п�ове�к� подкл�чен�� к Neon PostgreSQL"""
import asyncio
import sys
from database.database import get_engine
from sqlalchemy import text
from config import settings

async def test_connection():
    """��ове��т� подкл�чен�е к �азе данн��"""
    print(" ��ове�ка подкл�чен�� к Neon PostgreSQL...")
    print(f" DATABASE_URL: {settings.DATABASE_URL[:50]}..." if settings.DATABASE_URL else " DATABASE_URL не у�тановлен")
    print()
    
    if not settings.DATABASE_URL:
        print(" Ош��ка: DATABASE_URL не у�тановлен!")
        print(" У�танов�те пе�еменну� ок�ужен�� DATABASE_URL")
        print("   ���ме�: export DATABASE_URL='postgresql+asyncpg://user:pass@host/db'")
        return False
    
    if not settings.DATABASE_URL.startswith("postgresql"):
        print(f"  ��едуп�ежден�е: DATABASE_URL не �вл�ет�� PostgreSQL URL")
        print(f"   Теку��й фо�мат: {settings.DATABASE_URL.split('://')[0] if '://' in settings.DATABASE_URL else 'unknown'}")
        print()
    
    try:
        print("� �одкл�чен�е к �азе данн��...")
        engine = get_engine()
        
        async with engine.connect() as conn:
            # ��ове�ка ве���� PostgreSQL
            print(" ��ове�ка ве���� PostgreSQL...")
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f" �е���� PostgreSQL: {version.split(',')[0]}")
            
            # ��ове�ка теку�ей �аз� данн��
            print(" ��ове�ка теку�ей �аз� данн��...")
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f" Теку�а� Б�: {db_name}")
            
            # ��ове�ка теку�е�о пол�зовател�
            print(" ��ове�ка теку�е�о пол�зовател�...")
            result = await conn.execute(text("SELECT current_user"))
            user = result.scalar()
            print(f" Теку��й пол�зовател�: {user}")
            
            # ��ове�ка та�л�ц
            print(" ��ове�ка �у�е�тву���� та�л�ц...")
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            if tables:
                print(f" �айдено та�л�ц: {len(tables)}")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("  Та�л�ц� не найден� (�то но�мал�но дл� ново�о п�оекта)")
            
            print()
            print(" �одкл�чен�е к Neon у�пешно у�тановлено!")
            return True
            
    except ValueError as e:
        print(f" Ош��ка �н�ц�ал�зац��: {e}")
        print(" ��ове��те, что DATABASE_URL у�тановлен п�ав�л�но")
        return False
    except Exception as e:
        print(f" Ош��ка подкл�чен��: {e}")
        print()
        print(" �озможн�е п��ч�н�:")
        print("   1. �еп�ав�л�н�й фо�мат DATABASE_URL")
        print("   2. �еве�н�е учетн�е данн�е")
        print("   3. База данн�� недо�тупна")
        print("   4. ��о�лем� � �ет��")
        print()
        print(" ��ове��те �н�т�укц�� в NEON_SETUP.md")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)

