#!/bin/bash
# Скрипт для проверки подключения к серверу Yandex Cloud

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}Проверка подключения к серверу Yandex Cloud${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# IP адрес сервера (замените на ваш)
SERVER_IP="${1:-158.160.96.182}"
SERVER_USER="${2:-ubuntu}"

echo -e "${BLUE}Сервер: ${SERVER_USER}@${SERVER_IP}${NC}"
echo ""

# Проверка 1: Ping
echo -e "${BLUE}1. Проверка доступности сервера (ping)...${NC}"
if ping -c 3 -W 2 "$SERVER_IP" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Сервер доступен${NC}"
else
    echo -e "${RED}❌ Сервер недоступен${NC}"
    exit 1
fi

echo ""

# Проверка 2: SSH подключение
echo -e "${BLUE}2. Проверка SSH подключения...${NC}"
if ssh -o ConnectTimeout=5 -o BatchMode=yes "${SERVER_USER}@${SERVER_IP}" "echo 'SSH подключение работает'" 2>/dev/null; then
    echo -e "${GREEN}✅ SSH подключение работает${NC}"
else
    echo -e "${YELLOW}⚠️  SSH подключение требует аутентификацию${NC}"
    echo -e "${BLUE}   Попробуйте подключиться вручную:${NC}"
    echo -e "${BLUE}   ssh ${SERVER_USER}@${SERVER_IP}${NC}"
fi

echo ""

# Проверка 3: Проверка приложения на сервере (если SSH доступен)
echo -e "${BLUE}3. Проверка приложения на сервере...${NC}"
if ssh -o ConnectTimeout=5 "${SERVER_USER}@${SERVER_IP}" "cd ~/facy-app 2>/dev/null && docker compose -f docker-compose.prod.yml ps 2>/dev/null" 2>/dev/null; then
    echo -e "${GREEN}✅ Приложение найдено на сервере${NC}"
    
    # Проверка статуса контейнеров
    echo -e "${BLUE}   Статус контейнеров:${NC}"
    ssh -o ConnectTimeout=5 "${SERVER_USER}@${SERVER_IP}" "cd ~/facy-app && docker compose -f docker-compose.prod.yml ps" 2>/dev/null || true
    
    # Проверка подключения к базе данных на сервере
    echo ""
    echo -e "${BLUE}4. Проверка подключения к базе данных на сервере...${NC}"
    ssh -o ConnectTimeout=5 "${SERVER_USER}@${SERVER_IP}" "cd ~/facy-app && python3 check_connection.py 2>/dev/null" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Скрипт проверки не найден на сервере${NC}"
        echo -e "${BLUE}   Загрузите check_connection.py на сервер${NC}"
    }
else
    echo -e "${YELLOW}⚠️  Не удалось проверить приложение на сервере${NC}"
    echo -e "${BLUE}   Подключитесь к серверу вручную:${NC}"
    echo -e "${BLUE}   ssh ${SERVER_USER}@${SERVER_IP}${NC}"
fi

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}Проверка завершена${NC}"
echo -e "${BLUE}============================================================${NC}"

