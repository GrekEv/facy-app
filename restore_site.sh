#!/bin/bash
# Срочное восстановление сайта

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}СРОЧНОЕ ВОССТАНОВЛЕНИЕ САЙТА${NC}"
echo "=========================================="
echo ""

# Проверка, что на сервере
if [ ! -d "/home/ubuntu" ]; then
    echo -e "${RED}Этот скрипт должен быть запущен на сервере!${NC}"
    exit 1
fi

cd ~/facy-app || {
    echo -e "${RED}Директория ~/facy-app не найдена!${NC}"
    exit 1
}

echo -e "${BLUE}1. Проверка статуса приложения...${NC}"

# Проверка Docker
if command -v docker &> /dev/null; then
    if docker compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        echo -e "${GREEN}✓ Docker контейнеры запущены${NC}"
    else
        echo -e "${YELLOW}Запуск Docker контейнеров...${NC}"
        docker compose -f docker-compose.prod.yml up -d
    fi
else
    # Проверка Python процессов
    if pgrep -f "run_api.py\|main.py" > /dev/null; then
        echo -e "${GREEN}✓ Python процессы запущены${NC}"
    else
        echo -e "${YELLOW}Запуск приложения...${NC}"
        nohup python3 run_api.py > /tmp/api.log 2>&1 &
        nohup python3 main.py > /tmp/bot.log 2>&1 &
        sleep 2
    fi
fi

echo ""
echo -e "${BLUE}2. Проверка Nginx...${NC}"

if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx работает${NC}"
else
    echo -e "${YELLOW}Запуск Nginx...${NC}"
    sudo systemctl start nginx
fi

# Проверка конфигурации
if sudo nginx -t 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✓ Конфигурация Nginx корректна${NC}"
    sudo systemctl reload nginx
else
    echo -e "${RED}✗ Ошибка в конфигурации Nginx!${NC}"
    echo -e "${YELLOW}Восстановление базовой конфигурации...${NC}"
    
    APP_DIR=$(pwd)
    sudo tee /etc/nginx/sites-available/onlyface > /dev/null <<NGINX_EOF
server {
    listen 80;
    server_name onlyface.art www.onlyface.art;
    client_max_body_size 100M;

    location /static/ {
        alias ${APP_DIR}/static/;
    }
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
NGINX_EOF
    
    sudo rm -f /etc/nginx/sites-enabled/*
    sudo ln -sf /etc/nginx/sites-available/onlyface /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx
fi

echo ""
echo -e "${BLUE}3. Проверка портов...${NC}"

if sudo netstat -tlnp 2>/dev/null | grep -q ":8000"; then
    echo -e "${GREEN}✓ Порт 8000 открыт${NC}"
else
    echo -e "${RED}✗ Порт 8000 не слушается!${NC}"
fi

if sudo netstat -tlnp 2>/dev/null | grep -q ":80"; then
    echo -e "${GREEN}✓ Порт 80 открыт (Nginx)${NC}"
else
    echo -e "${RED}✗ Порт 80 не слушается!${NC}"
fi

echo ""
echo -e "${BLUE}4. Финальная проверка...${NC}"

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    echo -e "${GREEN}✓ Приложение отвечает на порту 8000${NC}"
else
    echo -e "${RED}✗ Приложение не отвечает на порту 8000${NC}"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -qE "200|301|302"; then
    echo -e "${GREEN}✓ Nginx проксирует запросы${NC}"
else
    echo -e "${RED}✗ Nginx не проксирует запросы${NC}"
fi

echo ""
echo -e "${GREEN}✓ Восстановление завершено${NC}"
echo ""
echo -e "${BLUE}Проверка доступности:${NC}"
echo "  curl -I http://localhost:8000/health"
echo "  curl -I http://localhost/"

