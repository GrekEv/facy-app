#!/bin/bash
# Скрипт для принудительного обновления контейнера с новым кодом

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ КОНТЕЙНЕРА ===${NC}"
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

echo -e "${BLUE}1. Обновление кода из репозитория...${NC}"
git fetch origin
git reset --hard origin/main
git pull origin main
echo -e "${GREEN}✓ Код обновлен${NC}"
echo ""

echo -e "${BLUE}2. Проверка что код обновился...${NC}"
if grep -q "@app.get(\"/api/health\")" api/main.py; then
    echo -e "${GREEN}✓ /api/health найден в коде${NC}"
else
    echo -e "${RED}✗ /api/health НЕ найден в коде!${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}3. Остановка и удаление старого контейнера...${NC}"
docker compose -f docker-compose.prod.yml stop api || true
docker compose -f docker-compose.prod.yml rm -f api || true
echo -e "${GREEN}✓ Старый контейнер удален${NC}"
echo ""

echo -e "${BLUE}4. Удаление старого образа...${NC}"
docker rmi facy-app-api 2>/dev/null || true
docker image prune -f
echo -e "${GREEN}✓ Старые образы удалены${NC}"
echo ""

echo -e "${BLUE}5. Сборка нового образа БЕЗ КЕША...${NC}"
docker compose -f docker-compose.prod.yml build --no-cache --pull api
echo -e "${GREEN}✓ Новый образ собран${NC}"
echo ""

echo -e "${BLUE}6. Запуск нового контейнера...${NC}"
docker compose -f docker-compose.prod.yml up -d api
echo -e "${GREEN}✓ Контейнер запущен${NC}"
echo ""

echo -e "${BLUE}7. Ожидание запуска (15 секунд)...${NC}"
sleep 15

echo -e "${BLUE}8. Проверка работы...${NC}"
echo ""
echo "Проверка /health:"
curl -s http://localhost:8000/health | python3 -m json.tool || curl -s http://localhost:8000/health
echo ""
echo ""
echo "Проверка /api/health:"
curl -s http://localhost:8000/api/health | python3 -m json.tool || curl -s http://localhost:8000/api/health
echo ""

echo -e "${GREEN}=== ГОТОВО ===${NC}"

