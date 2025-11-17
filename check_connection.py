#!/usr/bin/env python3
"""Скрипт для проверки подключения к серверу и базе данных на Yandex Cloud"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
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
    """Вывести сообщение с цветом"""
    if status == "success":
        print(f"{GREEN}✅ {message}{NC}")
    elif status == "error":
        print(f"{RED}❌ {message}{NC}")
    elif status == "warning":
        print(f"{YELLOW}⚠️  {message}{NC}")
    else:
        print(f"{BLUE}ℹ️  {message}{NC}")


async def check_database_connection():
    """Проверить подключение к базе данных"""
    print("\n" + "="*60)
    print_status("Проверка подключения к базе данных", "info")
    print("="*60)
    
    # Проверяем тип базы данных
    db_url = settings.DATABASE_URL
    print_status(f"URL базы данных: {db_url[:50]}...", "info")
    
    if db_url.startswith("sqlite"):
        print_status("Используется SQLite (локальная база данных)", "warning")
        print_status("Для продакшена рекомендуется PostgreSQL на Yandex Cloud", "warning")
        return False
    
    elif db_url.startswith("postgresql"):
        print_status("Обнаружено подключение к PostgreSQL", "success")
        
        # Извлекаем информацию о подключении
        try:
            # Парсим URL для отображения информации
            if "postgresql+asyncpg://" in db_url:
                db_url_clean = db_url.replace("postgresql+asyncpg://", "")
                if "@" in db_url_clean:
                    auth_part, host_part = db_url_clean.split("@", 1)
                    if ":" in auth_part:
                        user, password = auth_part.split(":", 1)
                        print_status(f"Пользователь: {user}", "info")
                        print_status(f"Хост: {host_part.split('/')[0].split('?')[0]}", "info")
                        if "yandexcloud.net" in host_part:
                            print_status("Подключение к Yandex Cloud PostgreSQL", "success")
                        else:
                            print_status("Подключение к внешнему PostgreSQL", "warning")
        except Exception as e:
            logger.debug(f"Не удалось распарсить URL: {e}")
        
        # Пытаемся подключиться
        try:
            print_status("Попытка подключения к базе данных...", "info")
            async with engine.begin() as conn:
                # Выполняем простой запрос
                result = await conn.execute(text("SELECT version(), current_database(), current_user"))
                row = result.fetchone()
                
                if row:
                    version, db_name, db_user = row
                    print_status("Подключение успешно!", "success")
                    print_status(f"PostgreSQL версия: {version}", "info")
                    print_status(f"База данных: {db_name}", "info")
                    print_status(f"Пользователь: {db_user}", "info")
                    
                    # Проверяем таблицы
                    result = await conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """))
                    tables = [row[0] for row in result.fetchall()]
                    
                    if tables:
                        print_status(f"Найдено таблиц: {len(tables)}", "success")
                        print_status(f"Таблицы: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}", "info")
                    else:
                        print_status("Таблицы не найдены (база данных пустая)", "warning")
                    
                    return True
                else:
                    print_status("Не удалось получить информацию о базе данных", "error")
                    return False
                    
        except Exception as e:
            print_status(f"Ошибка подключения к базе данных: {e}", "error")
            print_status("Проверьте:", "warning")
            print_status("  1. Правильность DATABASE_URL в .env файле", "warning")
            print_status("  2. Настройки групп безопасности в Yandex Cloud", "warning")
            print_status("  3. Доступность хоста PostgreSQL", "warning")
            print_status("  4. Правильность пароля и имени пользователя", "warning")
            return False
    
    else:
        print_status(f"Неизвестный тип базы данных: {db_url[:30]}...", "error")
        return False


def check_server_info():
    """Проверить информацию о сервере"""
    print("\n" + "="*60)
    print_status("Информация о сервере", "info")
    print("="*60)
    
    import socket
    hostname = socket.gethostname()
    print_status(f"Имя хоста: {hostname}", "info")
    
    try:
        # Пытаемся получить внешний IP
        import urllib.request
        external_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
        print_status(f"Внешний IP: {external_ip}", "info")
    except Exception as e:
        logger.debug(f"Не удалось получить внешний IP: {e}")
    
    # Проверяем переменные окружения
    print_status("Переменные окружения:", "info")
    print_status(f"  ENVIRONMENT: {settings.ENVIRONMENT}", "info")
    print_status(f"  HOST: {settings.HOST}", "info")
    print_status(f"  PORT: {settings.port}", "info")
    
    if settings.BOT_TOKEN:
        print_status(f"  BOT_TOKEN: {'*' * 20}...{settings.BOT_TOKEN[-10:]}", "info")
    else:
        print_status("  BOT_TOKEN: не установлен", "warning")
    
    # Используем webapp_url для автоматического определения
    webapp_url = settings.webapp_url
    print_status(f"  WEBAPP_URL: {webapp_url}", "info")
    if not settings.WEBAPP_URL:
        print_status("  (автоматически определен)", "info")


async def main():
    """Основная функция"""
    print("\n" + "="*60)
    print_status("Проверка подключения к Yandex Cloud", "info")
    print("="*60)
    
    # Проверяем информацию о сервере
    check_server_info()
    
    # Проверяем подключение к базе данных
    db_connected = await check_database_connection()
    
    # Итоговый результат
    print("\n" + "="*60)
    print_status("Результаты проверки", "info")
    print("="*60)
    
    if db_connected:
        print_status("База данных: Подключена к PostgreSQL на Yandex Cloud", "success")
    else:
        print_status("База данных: Не подключена или использует SQLite", "error")
    
    print("\n" + "="*60)
    
    if db_connected:
        print_status("Все проверки пройдены успешно! ✅", "success")
        return 0
    else:
        print_status("Обнаружены проблемы. Проверьте настройки.", "error")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nПроверка прервана пользователем", "warning")
        sys.exit(1)
    except Exception as e:
        print_status(f"Критическая ошибка: {e}", "error")
        import traceback
        traceback.print_exc()
        sys.exit(1)

