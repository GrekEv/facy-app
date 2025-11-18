#!/usr/bin/env python3
"""�к��пт дл� п�ове�к� подкл�чен�� к �е�ве�у � �азе данн�� на Yandex Cloud"""

import asyncio
import sys
import os
from pathlib import Path

# �о�авл�ем теку�у� д��екто��� в пут�
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from database.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def print_status(message: str, status: str = "info"):
    """��ве�т� �оо��ен�е � цветом"""
    if status == "success":
        print(f"{GREEN} {message}{NC}")
    elif status == "error":
        print(f"{RED} {message}{NC}")
    elif status == "warning":
        print(f"{YELLOW}  {message}{NC}")
    else:
        print(f"{BLUE}��  {message}{NC}")


async def check_database_connection():
    """��ове��т� подкл�чен�е к �азе данн��"""
    print("\n" + "="*60)
    print_status("��ове�ка подкл�чен�� к �азе данн��", "info")
    print("="*60)
    
    # ��ове��ем т�п �аз� данн��
    db_url = settings.DATABASE_URL
    print_status(f"URL �аз� данн��: {db_url[:50]}...", "info")
    
    if db_url.startswith("sqlite"):
        print_status("И�пол�зует�� SQLite (локал�на� �аза данн��)", "warning")
        print_status("�л� п�одакшена �екомендует�� PostgreSQL на Yandex Cloud", "warning")
        return False
    
    elif db_url.startswith("postgresql"):
        print_status("О�на�ужено подкл�чен�е к PostgreSQL", "success")
        
        # Извлекаем �нфо�мац�� о подкл�чен��
        try:
            # �а���м URL дл� ото��ажен�� �нфо�мац��
            if "postgresql+asyncpg://" in db_url:
                db_url_clean = db_url.replace("postgresql+asyncpg://", "")
                if "@" in db_url_clean:
                    auth_part, host_part = db_url_clean.split("@", 1)
                    if ":" in auth_part:
                        user, password = auth_part.split(":", 1)
                        print_status(f"�ол�зовател�: {user}", "info")
                        print_status(f"�о�т: {host_part.split('/')[0].split('?')[0]}", "info")
                        if "yandexcloud.net" in host_part:
                            print_status("�одкл�чен�е к Yandex Cloud PostgreSQL", "success")
                        else:
                            print_status("�одкл�чен�е к внешнему PostgreSQL", "warning")
        except Exception as e:
            logger.debug(f"�е удало�� �а�па���т� URL: {e}")
        
        # ��таем�� подкл�ч�т���
        try:
            print_status("�оп�тка подкл�чен�� к �азе данн��...", "info")
            async with engine.begin() as conn:
                # ��полн�ем п�о�той зап�о�
                result = await conn.execute(text("SELECT version(), current_database(), current_user"))
                row = result.fetchone()
                
                if row:
                    version, db_name, db_user = row
                    print_status("�одкл�чен�е у�пешно!", "success")
                    print_status(f"PostgreSQL ве����: {version}", "info")
                    print_status(f"База данн��: {db_name}", "info")
                    print_status(f"�ол�зовател�: {db_user}", "info")
                    
                    # ��ове��ем та�л�ц�
                    result = await conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """))
                    tables = [row[0] for row in result.fetchall()]
                    
                    if tables:
                        print_status(f"�айдено та�л�ц: {len(tables)}", "success")
                        print_status(f"Та�л�ц�: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}", "info")
                    else:
                        print_status("Та�л�ц� не найден� (�аза данн�� пу�та�)", "warning")
                    
                    return True
                else:
                    print_status("�е удало�� получ�т� �нфо�мац�� о �азе данн��", "error")
                    return False
                    
        except Exception as e:
            print_status(f"Ош��ка подкл�чен�� к �азе данн��: {e}", "error")
            print_status("��ове��те:", "warning")
            print_status("  1. ��ав�л�но�т� DATABASE_URL в .env файле", "warning")
            print_status("  2. �а�т�ойк� ��упп �езопа�но�т� в Yandex Cloud", "warning")
            print_status("  3. �о�тупно�т� �о�та PostgreSQL", "warning")
            print_status("  4. ��ав�л�но�т� па�ол� � �мен� пол�зовател�", "warning")
            return False
    
    else:
        print_status(f"�е�зве�тн�й т�п �аз� данн��: {db_url[:30]}...", "error")
        return False


def check_server_info():
    """��ове��т� �нфо�мац�� о �е�ве�е"""
    print("\n" + "="*60)
    print_status("Инфо�мац�� о �е�ве�е", "info")
    print("="*60)
    
    import socket
    hostname = socket.gethostname()
    print_status(f"Им� �о�та: {hostname}", "info")
    
    try:
        # ��таем�� получ�т� внешн�й IP
        import urllib.request
        external_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
        print_status(f"�нешн�й IP: {external_ip}", "info")
    except Exception as e:
        logger.debug(f"�е удало�� получ�т� внешн�й IP: {e}")
    
    # ��ове��ем пе�еменн�е ок�ужен��
    print_status("�е�еменн�е ок�ужен��:", "info")
    print_status(f"  ENVIRONMENT: {settings.ENVIRONMENT}", "info")
    print_status(f"  HOST: {settings.HOST}", "info")
    print_status(f"  PORT: {settings.port}", "info")
    
    if settings.BOT_TOKEN:
        print_status(f"  BOT_TOKEN: {'*' * 20}...{settings.BOT_TOKEN[-10:]}", "info")
    else:
        print_status("  BOT_TOKEN: не у�тановлен", "warning")
    
    # И�пол�зуем webapp_url дл� автомат�че�ко�о оп�еделен��
    webapp_url = settings.webapp_url
    print_status(f"  WEBAPP_URL: {webapp_url}", "info")
    if not settings.WEBAPP_URL:
        print_status("  (автомат�че�к� оп�еделен)", "info")


async def main():
    """О�новна� функц��"""
    print("\n" + "="*60)
    print_status("��ове�ка подкл�чен�� к Yandex Cloud", "info")
    print("="*60)
    
    # ��ове��ем �нфо�мац�� о �е�ве�е
    check_server_info()
    
    # ��ове��ем подкл�чен�е к �азе данн��
    db_connected = await check_database_connection()
    
    # Ито�ов�й �езул�тат
    print("\n" + "="*60)
    print_status("�езул�тат� п�ове�к�", "info")
    print("="*60)
    
    if db_connected:
        print_status("База данн��: �одкл�чена к PostgreSQL на Yandex Cloud", "success")
    else:
        print_status("База данн��: �е подкл�чена �л� ��пол�зует SQLite", "error")
    
    print("\n" + "="*60)
    
    if db_connected:
        print_status("��е п�ове�к� п�ойден� у�пешно! ", "success")
        return 0
    else:
        print_status("О�на�ужен� п�о�лем�. ��ове��те на�т�ойк�.", "error")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\n��ове�ка п�е�вана пол�зователем", "warning")
        sys.exit(1)
    except Exception as e:
        print_status(f"���т�че�ка� ош��ка: {e}", "error")
        import traceback
        traceback.print_exc()
        sys.exit(1)

