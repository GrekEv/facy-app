#!/bin/bash
# Скрипт для диагностики и запуска API на сервере

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== ДИАГНОСТИКА И ЗАПУСК API ===${NC}"
echo ""

# Определяем директорию приложения
APP_DIRS=("~/facy-app" "/home/ubuntu/facy-app" "/root/facy-app" "$(pwd)")
APP_DIR=""

for dir in "${APP_DIRS[@]}"; do
    expanded_dir=$(eval echo "$dir")
    if [ -d "$expanded_dir" ] && [ -f "$expanded_dir/docker-compose.prod.yml" ]; then
        APP_DIR="$expanded_dir"
        break
    fi
done

if [ -z "$APP_DIR" ]; then
    echo -e "${RED}Директория приложения не найдена!${NC}"
    echo "Ищем в: ${APP_DIRS[*]}"
    exit 1
fi

echo -e "${GREEN}Найдена директория: $APP_DIR${NC}"
cd "$APP_DIR"

echo ""
echo -e "${BLUE}1. Проверка Docker контейнеров...${NC}"
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo -e "${RED}Docker Compose не найден!${NC}"
    exit 1
fi
$DOCKER_COMPOSE -f docker-compose.prod.yml ps

echo ""
echo -e "${BLUE}2. Проверка файлов...${NC}"
if [ ! -f "run_api.py" ]; then
    echo -e "${RED}run_api.py не найден в $APP_DIR${NC}"
    echo "Текущая директория: $(pwd)"
    echo "Файлы в директории:"
    ls -la | head -10
    exit 1
else
    echo -e "${GREEN}✓ run_api.py найден${NC}"
fi

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env файл не найден${NC}"
    echo "Создайте .env файл с необходимыми переменными"
else
    echo -e "${GREEN}✓ .env файл найден${NC}"
fi

echo ""
echo -e "${BLUE}3. Проверка порта 8000...${NC}"
if lsof -i :8000 2>/dev/null | grep -q LISTEN; then
    echo -e "${YELLOW}⚠ Порт 8000 уже занят${NC}"
    lsof -i :8000
else
    echo -e "${GREEN}✓ Порт 8000 свободен${NC}"
fi

echo ""
echo -e "${BLUE}4. Запуск Docker контейнеров...${NC}"
$DOCKER_COMPOSE -f docker-compose.prod.yml down 2>/dev/null || true
$DOCKER_COMPOSE -f docker-compose.prod.yml up -d

echo ""
echo -e "${BLUE}5. Ожидание запуска (30 секунд)...${NC}"
sleep 30

echo ""
echo -e "${BLUE}6. Проверка статуса контейнеров...${NC}"
$DOCKER_COMPOSE -f docker-compose.prod.yml ps

echo ""
echo -e "${BLUE}7. Проверка логов API...${NC}"
$DOCKER_COMPOSE -f docker-compose.prod.yml logs api --tail=20

echo ""
echo -e "${BLUE}8. Проверка health endpoint...${NC}"
sleep 5
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API работает!${NC}"
    curl -s http://localhost:8000/health | head -3
else
    echo -e "${RED}✗ API не отвечает${NC}"
    echo "Проверьте логи: $DOCKER_COMPOSE -f docker-compose.prod.yml logs api"
fi

echo ""
echo -e "${BLUE}9. Проверка API health...${NC}"
curl -s http://localhost:8000/api/health | head -5

echo ""
echo -e "${GREEN}=== ГОТОВО ===${NC}"
echo ""
echo "Команды для проверки:"
echo "  $DOCKER_COMPOSE -f docker-compose.prod.yml ps"
echo "  $DOCKER_COMPOSE -f docker-compose.prod.yml logs -f api"
echo "  curl http://localhost:8000/health"

