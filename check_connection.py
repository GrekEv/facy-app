#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Скрипт для проверки подключения к серверу и базе данных на Yandex Cloud"""

import asyncio
import sys
import os
from pathlib import Path

# ÃÃÂ¾ÃÃÂ°ÃÂ²ÃÂ»ÃÃÂµÃÂ¼ ÃÂÃÂµÃÂºÃÂÃÃÂÃ ÃÂ´ÃÃÃÂµÃÂºÃÂÃÂ¾ÃÃÃ ÃÂ² ÃÂ¿ÃÂÃÂÃ
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
    """ÃÃÃÂ²ÃÂµÃÃÂÃ ÃÃÂ¾ÃÂ¾ÃÃÃÂµÃÂ½ÃÃÂµ Ã ÃÂÃÂ²ÃÂµÃÂÃÂ¾ÃÂ¼"""
    if status == "success":
        print(f"{GREEN} {message}{NC}")
    elif status == "error":
        print(f"{RED} {message}{NC}")
    elif status == "warning":
        print(f"{YELLOW}  {message}{NC}")
    else:
        print(f"{BLUE}ÂÂ¹  {message}{NC}")


async def check_database_connection():
    """ÃÃÃÂ¾ÃÂ²ÃÂµÃÃÃÂÃ ÃÂ¿ÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÃÂµ ÃÂº ÃÃÂ°ÃÂ·ÃÂµ ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ"""
    print("\n" + "="*60)
    print_status("ÃÃÃÂ¾ÃÂ²ÃÂµÃÃÂºÃÂ° ÃÂ¿ÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÃ ÃÂº ÃÃÂ°ÃÂ·ÃÂµ ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ", "info")
    print("="*60)
    
    # ÃÃÃÂ¾ÃÂ²ÃÂµÃÃÃÂµÃÂ¼ ÃÂÃÃÂ¿ ÃÃÂ°ÃÂ·Ã ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ
    db_url = settings.DATABASE_URL
    print_status(f"URL ÃÃÂ°ÃÂ·Ã ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ: {db_url[:50]}...", "info")
    
    if db_url.startswith("sqlite"):
        print_status("ÃÂÃÃÂ¿ÃÂ¾ÃÂ»ÃÃÂ·ÃÂÃÂµÃÂÃÃ SQLite (ÃÂ»ÃÂ¾ÃÂºÃÂ°ÃÂ»ÃÃÂ½ÃÂ°Ã ÃÃÂ°ÃÂ·ÃÂ° ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ)", "warning")
        print_status("ÃÃÂ»Ã ÃÂ¿ÃÃÂ¾ÃÂ´ÃÂ°ÃÂºÃÂÃÂµÃÂ½ÃÂ° ÃÃÂµÃÂºÃÂ¾ÃÂ¼ÃÂµÃÂ½ÃÂ´ÃÂÃÂµÃÂÃÃ PostgreSQL ÃÂ½ÃÂ° Yandex Cloud", "warning")
        return False
    
    elif db_url.startswith("postgresql"):
        print_status("ÃÂÃÃÂ½ÃÂ°ÃÃÂÃÂ¶ÃÂµÃÂ½ÃÂ¾ ÃÂ¿ÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÃÂµ ÃÂº PostgreSQL", "success")
        
        # ÃÂÃÂ·ÃÂ²ÃÂ»ÃÂµÃÂºÃÂ°ÃÂµÃÂ¼ ÃÃÂ½ÃÂÃÂ¾ÃÃÂ¼ÃÂ°ÃÂÃÃ ÃÂ¾ ÃÂ¿ÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÃ
        try:
            # ÃÃÂ°ÃÃÃÃÂ¼ URL ÃÂ´ÃÂ»Ã ÃÂ¾ÃÂÃÂ¾ÃÃÃÂ°ÃÂ¶ÃÂµÃÂ½ÃÃ ÃÃÂ½ÃÂÃÂ¾ÃÃÂ¼ÃÂ°ÃÂÃÃ
            if "postgresql+asyncpg://" in db_url:
                db_url_clean = db_url.replace("postgresql+asyncpg://", "")
                if "@" in db_url_clean:
                    auth_part, host_part = db_url_clean.split("@", 1)
                    if ":" in auth_part:
                        user, password = auth_part.split(":", 1)
                        print_status(f"ÃÃÂ¾ÃÂ»ÃÃÂ·ÃÂ¾ÃÂ²ÃÂ°ÃÂÃÂµÃÂ»Ã: {user}", "info")
                        print_status(f"ÃÃÂ¾ÃÃÂ: {host_part.split('/')[0].split('?')[0]}", "info")
                        if "yandexcloud.net" in host_part:
                            print_status("ÃÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÃÂµ ÃÂº Yandex Cloud PostgreSQL", "success")
                        else:
                            print_status("ÃÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÃÂµ ÃÂº ÃÂ²ÃÂ½ÃÂµÃÂÃÂ½ÃÂµÃÂ¼ÃÂ PostgreSQL", "warning")
        except Exception as e:
            logger.debug(f"ÃÃÂµ ÃÂÃÂ´ÃÂ°ÃÂ»ÃÂ¾ÃÃ ÃÃÂ°ÃÃÂ¿ÃÂ°ÃÃÃÃÂÃ URL: {e}")
        
        # ÃÃÃÂÃÂ°ÃÂµÃÂ¼ÃÃ ÃÂ¿ÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÃÂÃÃÃ
        try:
            print_status("ÃÃÂ¾ÃÂ¿ÃÃÂÃÂºÃÂ° ÃÂ¿ÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÃ ÃÂº ÃÃÂ°ÃÂ·ÃÂµ ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ...", "info")
            async with engine.begin() as conn:
                # ÃÃÃÂ¿ÃÂ¾ÃÂ»ÃÂ½ÃÃÂµÃÂ¼ ÃÂ¿ÃÃÂ¾ÃÃÂÃÂ¾ÃÂ¹ ÃÂ·ÃÂ°ÃÂ¿ÃÃÂ¾Ã
                result = await conn.execute(text("SELECT version(), current_database(), current_user"))
                row = result.fetchone()
                
                if row:
                    version, db_name, db_user = row
                    print_status("ÃÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÃÂµ ÃÂÃÃÂ¿ÃÂµÃÂÃÂ½ÃÂ¾!", "success")
                    print_status(f"PostgreSQL ÃÂ²ÃÂµÃÃÃÃ: {version}", "info")
                    print_status(f"ÃÂÃÂ°ÃÂ·ÃÂ° ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ: {db_name}", "info")
                    print_status(f"ÃÃÂ¾ÃÂ»ÃÃÂ·ÃÂ¾ÃÂ²ÃÂ°ÃÂÃÂµÃÂ»Ã: {db_user}", "info")
                    
                    # ÃÃÃÂ¾ÃÂ²ÃÂµÃÃÃÂµÃÂ¼ ÃÂÃÂ°ÃÃÂ»ÃÃÂÃ
                    result = await conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """))
                    tables = [row[0] for row in result.fetchall()]
                    
                    if tables:
                        print_status(f"ÃÃÂ°ÃÂ¹ÃÂ´ÃÂµÃÂ½ÃÂ¾ ÃÂÃÂ°ÃÃÂ»ÃÃÂ: {len(tables)}", "success")
                        print_status(f"ÃÂ¢ÃÂ°ÃÃÂ»ÃÃÂÃ: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}", "info")
                    else:
                        print_status("ÃÂ¢ÃÂ°ÃÃÂ»ÃÃÂÃ ÃÂ½ÃÂµ ÃÂ½ÃÂ°ÃÂ¹ÃÂ´ÃÂµÃÂ½Ã (ÃÃÂ°ÃÂ·ÃÂ° ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ ÃÂ¿ÃÂÃÃÂÃÂ°Ã)", "warning")
                    
                    return True
                else:
                    print_status("ÃÃÂµ ÃÂÃÂ´ÃÂ°ÃÂ»ÃÂ¾ÃÃ ÃÂ¿ÃÂ¾ÃÂ»ÃÂÃÂÃÃÂÃ ÃÃÂ½ÃÂÃÂ¾ÃÃÂ¼ÃÂ°ÃÂÃÃ ÃÂ¾ ÃÃÂ°ÃÂ·ÃÂµ ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ", "error")
                    return False
                    
        except Exception as e:
            print_status(f"ÃÂÃÂÃÃÃÂºÃÂ° ÃÂ¿ÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÃ ÃÂº ÃÃÂ°ÃÂ·ÃÂµ ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ: {e}", "error")
            print_status("ÃÃÃÂ¾ÃÂ²ÃÂµÃÃÃÂÃÂµ:", "warning")
            print_status("  1. ÃÃÃÂ°ÃÂ²ÃÃÂ»ÃÃÂ½ÃÂ¾ÃÃÂÃ DATABASE_URL ÃÂ² .env ÃÂÃÂ°ÃÂ¹ÃÂ»ÃÂµ", "warning")
            print_status("  2. ÃÃÂ°ÃÃÂÃÃÂ¾ÃÂ¹ÃÂºÃ ÃÃÃÂÃÂ¿ÃÂ¿ ÃÃÂµÃÂ·ÃÂ¾ÃÂ¿ÃÂ°ÃÃÂ½ÃÂ¾ÃÃÂÃ ÃÂ² Yandex Cloud", "warning")
            print_status("  3. ÃÃÂ¾ÃÃÂÃÂÃÂ¿ÃÂ½ÃÂ¾ÃÃÂÃ ÃÃÂ¾ÃÃÂÃÂ° PostgreSQL", "warning")
            print_status("  4. ÃÃÃÂ°ÃÂ²ÃÃÂ»ÃÃÂ½ÃÂ¾ÃÃÂÃ ÃÂ¿ÃÂ°ÃÃÂ¾ÃÂ»Ã Ã ÃÃÂ¼ÃÂµÃÂ½Ã ÃÂ¿ÃÂ¾ÃÂ»ÃÃÂ·ÃÂ¾ÃÂ²ÃÂ°ÃÂÃÂµÃÂ»Ã", "warning")
            return False
    
    else:
        print_status(f"ÃÃÂµÃÃÂ·ÃÂ²ÃÂµÃÃÂÃÂ½ÃÃÂ¹ ÃÂÃÃÂ¿ ÃÃÂ°ÃÂ·Ã ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ: {db_url[:30]}...", "error")
        return False


def check_server_info():
    """ÃÃÃÂ¾ÃÂ²ÃÂµÃÃÃÂÃ ÃÃÂ½ÃÂÃÂ¾ÃÃÂ¼ÃÂ°ÃÂÃÃ ÃÂ¾ ÃÃÂµÃÃÂ²ÃÂµÃÃÂµ"""
    print("\n" + "="*60)
    print_status("ÃÂÃÂ½ÃÂÃÂ¾ÃÃÂ¼ÃÂ°ÃÂÃÃ ÃÂ¾ ÃÃÂµÃÃÂ²ÃÂµÃÃÂµ", "info")
    print("="*60)
    
    import socket
    hostname = socket.gethostname()
    print_status(f"ÃÂÃÂ¼Ã ÃÃÂ¾ÃÃÂÃÂ°: {hostname}", "info")
    
    try:
        # ÃÃÃÂÃÂ°ÃÂµÃÂ¼ÃÃ ÃÂ¿ÃÂ¾ÃÂ»ÃÂÃÂÃÃÂÃ ÃÂ²ÃÂ½ÃÂµÃÂÃÂ½ÃÃÂ¹ IP
        import urllib.request
        external_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
        print_status(f"ÃÃÂ½ÃÂµÃÂÃÂ½ÃÃÂ¹ IP: {external_ip}", "info")
    except Exception as e:
        logger.debug(f"ÃÃÂµ ÃÂÃÂ´ÃÂ°ÃÂ»ÃÂ¾ÃÃ ÃÂ¿ÃÂ¾ÃÂ»ÃÂÃÂÃÃÂÃ ÃÂ²ÃÂ½ÃÂµÃÂÃÂ½ÃÃÂ¹ IP: {e}")
    
    # ÃÃÃÂ¾ÃÂ²ÃÂµÃÃÃÂµÃÂ¼ ÃÂ¿ÃÂµÃÃÂµÃÂ¼ÃÂµÃÂ½ÃÂ½ÃÃÂµ ÃÂ¾ÃÂºÃÃÂÃÂ¶ÃÂµÃÂ½ÃÃ
    print_status("ÃÃÂµÃÃÂµÃÂ¼ÃÂµÃÂ½ÃÂ½ÃÃÂµ ÃÂ¾ÃÂºÃÃÂÃÂ¶ÃÂµÃÂ½ÃÃ:", "info")
    print_status(f"  ENVIRONMENT: {settings.ENVIRONMENT}", "info")
    print_status(f"  HOST: {settings.HOST}", "info")
    print_status(f"  PORT: {settings.port}", "info")
    
    if settings.BOT_TOKEN:
        print_status(f"  BOT_TOKEN: {'*' * 20}...{settings.BOT_TOKEN[-10:]}", "info")
    else:
        print_status("  BOT_TOKEN: ÃÂ½ÃÂµ ÃÂÃÃÂÃÂ°ÃÂ½ÃÂ¾ÃÂ²ÃÂ»ÃÂµÃÂ½", "warning")
    
    # ÃÂÃÃÂ¿ÃÂ¾ÃÂ»ÃÃÂ·ÃÂÃÂµÃÂ¼ webapp_url ÃÂ´ÃÂ»Ã ÃÂ°ÃÂ²ÃÂÃÂ¾ÃÂ¼ÃÂ°ÃÂÃÃÂÃÂµÃÃÂºÃÂ¾ÃÃÂ¾ ÃÂ¾ÃÂ¿ÃÃÂµÃÂ´ÃÂµÃÂ»ÃÂµÃÂ½ÃÃ
    webapp_url = settings.webapp_url
    print_status(f"  WEBAPP_URL: {webapp_url}", "info")
    if not settings.WEBAPP_URL:
        print_status("  (ÃÂ°ÃÂ²ÃÂÃÂ¾ÃÂ¼ÃÂ°ÃÂÃÃÂÃÂµÃÃÂºÃ ÃÂ¾ÃÂ¿ÃÃÂµÃÂ´ÃÂµÃÂ»ÃÂµÃÂ½)", "info")


async def main():
    """ÃÂÃÃÂ½ÃÂ¾ÃÂ²ÃÂ½ÃÂ°Ã ÃÂÃÂÃÂ½ÃÂºÃÂÃÃ"""
    print("\n" + "="*60)
    print_status("ÃÃÃÂ¾ÃÂ²ÃÂµÃÃÂºÃÂ° ÃÂ¿ÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÃ ÃÂº Yandex Cloud", "info")
    print("="*60)
    
    # ÃÃÃÂ¾ÃÂ²ÃÂµÃÃÃÂµÃÂ¼ ÃÃÂ½ÃÂÃÂ¾ÃÃÂ¼ÃÂ°ÃÂÃÃ ÃÂ¾ ÃÃÂµÃÃÂ²ÃÂµÃÃÂµ
    check_server_info()
    
    # ÃÃÃÂ¾ÃÂ²ÃÂµÃÃÃÂµÃÂ¼ ÃÂ¿ÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÃÂµ ÃÂº ÃÃÂ°ÃÂ·ÃÂµ ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ
    db_connected = await check_database_connection()
    
    # ÃÂÃÂÃÂ¾ÃÃÂ¾ÃÂ²ÃÃÂ¹ ÃÃÂµÃÂ·ÃÂÃÂ»ÃÃÂÃÂ°ÃÂ
    print("\n" + "="*60)
    print_status("ÃÃÂµÃÂ·ÃÂÃÂ»ÃÃÂÃÂ°ÃÂÃ ÃÂ¿ÃÃÂ¾ÃÂ²ÃÂµÃÃÂºÃ", "info")
    print("="*60)
    
    if db_connected:
        print_status("ÃÂÃÂ°ÃÂ·ÃÂ° ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ: ÃÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÂ° ÃÂº PostgreSQL ÃÂ½ÃÂ° Yandex Cloud", "success")
    else:
        print_status("ÃÂÃÂ°ÃÂ·ÃÂ° ÃÂ´ÃÂ°ÃÂ½ÃÂ½ÃÃ: ÃÃÂµ ÃÂ¿ÃÂ¾ÃÂ´ÃÂºÃÂ»ÃÃÂÃÂµÃÂ½ÃÂ° ÃÃÂ»Ã ÃÃÃÂ¿ÃÂ¾ÃÂ»ÃÃÂ·ÃÂÃÂµÃÂ SQLite", "error")
    
    print("\n" + "="*60)
    
    if db_connected:
        print_status("ÃÃÃÂµ ÃÂ¿ÃÃÂ¾ÃÂ²ÃÂµÃÃÂºÃ ÃÂ¿ÃÃÂ¾ÃÂ¹ÃÂ´ÃÂµÃÂ½Ã ÃÂÃÃÂ¿ÃÂµÃÂÃÂ½ÃÂ¾! ", "success")
        return 0
    else:
        print_status("ÃÂÃÃÂ½ÃÂ°ÃÃÂÃÂ¶ÃÂµÃÂ½Ã ÃÂ¿ÃÃÂ¾ÃÃÂ»ÃÂµÃÂ¼Ã. ÃÃÃÂ¾ÃÂ²ÃÂµÃÃÃÂÃÂµ ÃÂ½ÃÂ°ÃÃÂÃÃÂ¾ÃÂ¹ÃÂºÃ.", "error")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nÃÃÃÂ¾ÃÂ²ÃÂµÃÃÂºÃÂ° ÃÂ¿ÃÃÂµÃÃÂ²ÃÂ°ÃÂ½ÃÂ° ÃÂ¿ÃÂ¾ÃÂ»ÃÃÂ·ÃÂ¾ÃÂ²ÃÂ°ÃÂÃÂµÃÂ»ÃÂµÃÂ¼", "warning")
        sys.exit(1)
    except Exception as e:
        print_status(f"ÃÃÃÃÂÃÃÂÃÂµÃÃÂºÃÂ°Ã ÃÂ¾ÃÂÃÃÃÂºÃÂ°: {e}", "error")
        import traceback
        traceback.print_exc()
        sys.exit(1)

