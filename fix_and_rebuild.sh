#!/bin/bash
# Скрипт для исправления файлов с кодировкой и пересборки контейнера

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== ИСПРАВЛЕНИЕ ФАЙЛОВ И ПЕРЕСБОРКА КОНТЕЙНЕРА ===${NC}"
echo ""

# Проверка что на сервере
if [ ! -d "/home/ubuntu" ]; then
    echo -e "${RED}Этот скрипт должен быть запущен на сервере!${NC}"
    exit 1
fi

cd ~/facy-app || {
    echo -e "${RED}Директория ~/facy-app не найдена!${NC}"
    exit 1
}

echo -e "${BLUE}1. Остановка контейнера...${NC}"
docker compose -f docker-compose.prod.yml stop api 2>/dev/null || true
docker compose -f docker-compose.prod.yml rm -f api 2>/dev/null || true
echo -e "${GREEN}✓ Контейнер остановлен${NC}"
echo ""

echo -e "${BLUE}2. Освобождение порта 8000...${NC}"
sudo fuser -k 8000/tcp 2>/dev/null || echo "Порт свободен"
echo -e "${GREEN}✓ Порт освобожден${NC}"
echo ""

echo -e "${BLUE}3. Исправление database/__init__.py...${NC}"
python3 << 'PYEOF'
content = '''# -*- coding: utf-8 -*-
"""Модуль базы данных"""
from .models import Base, User, Generation, Transaction
from .database import init_db, get_session

__all__ = ["Base", "User", "Generation", "Transaction", "init_db", "get_session"]
'''
with open('database/__init__.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ database/__init__.py исправлен")
PYEOF

# Проверка
if head -1 database/__init__.py | grep -q "coding: utf-8"; then
    echo -e "${GREEN}✓ Файл исправлен${NC}"
else
    echo -e "${RED}✗ Ошибка исправления файла${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}4. Проверка других файлов...${NC}"
if ! head -1 run_api.py | grep -q "coding: utf-8"; then
    echo -e "${YELLOW}Исправление run_api.py...${NC}"
    sed -i '1i# -*- coding: utf-8 -*-' run_api.py
fi

if ! head -1 database/models.py | grep -q "coding: utf-8"; then
    echo -e "${YELLOW}Исправление database/models.py...${NC}"
    sed -i '1i# -*- coding: utf-8 -*-' database/models.py
fi
echo -e "${GREEN}✓ Все файлы проверены${NC}"
echo ""

echo -e "${BLUE}5. Удаление старого образа...${NC}"
docker rmi facy-app-api 2>/dev/null || true
echo -e "${GREEN}✓ Старый образ удален${NC}"
echo ""

echo -e "${BLUE}6. Сборка нового образа БЕЗ КЕША...${NC}"
docker compose -f docker-compose.prod.yml build --no-cache api
echo -e "${GREEN}✓ Образ собран${NC}"
echo ""

echo -e "${BLUE}7. Запуск контейнера...${NC}"
docker compose -f docker-compose.prod.yml up -d api
echo -e "${GREEN}✓ Контейнер запущен${NC}"
echo ""

echo -e "${BLUE}8. Ожидание запуска (15 секунд)...${NC}"
sleep 15

echo -e "${BLUE}9. Проверка логов...${NC}"
docker logs facy-api --tail 20
echo ""

echo -e "${BLUE}10. Проверка порта 8000...${NC}"
if sudo ss -tlnp | grep -q ":8000"; then
    echo -e "${GREEN}✓ Порт 8000 слушается${NC}"
else
    echo -e "${YELLOW}⚠ Порт 8000 не слушается${NC}"
fi
echo ""

echo -e "${BLUE}11. Проверка работы приложения...${NC}"
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo "")
if [ -n "$HEALTH" ]; then
    echo -e "${GREEN}✓ Приложение работает!${NC}"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
else
    echo -e "${RED}✗ Приложение не отвечает${NC}"
fi
echo ""

echo -e "${GREEN}=== ГОТОВО ===${NC}"

