#!/bin/bash
# Скрипт для исправления проблемы с Nginx на порту 80

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Исправление проблемы с Nginx на порту 80${NC}"
echo "=========================================="
echo ""

# Проверка, что на сервере
if [ ! -d "/home/ubuntu" ]; then
    echo -e "${RED}Этот скрипт должен быть запущен на сервере!${NC}"
    exit 1
fi

echo -e "${BLUE}1. Проверка статуса Nginx...${NC}"
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx работает${NC}"
else
    echo -e "${YELLOW}Запуск Nginx...${NC}"
    sudo systemctl start nginx
    sudo systemctl enable nginx
fi

echo ""
echo -e "${BLUE}2. Проверка конфигурации...${NC}"
if sudo nginx -t 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✓ Конфигурация корректна${NC}"
    sudo systemctl reload nginx
else
    echo -e "${RED}✗ Ошибка в конфигурации!${NC}"
    sudo nginx -t
    exit 1
fi

echo ""
echo -e "${BLUE}3. Проверка портов...${NC}"
if sudo netstat -tlnp 2>/dev/null | grep -q ":80 "; then
    echo -e "${GREEN}✓ Порт 80 слушается${NC}"
else
    echo -e "${YELLOW}Порт 80 не слушается, проверяю firewall...${NC}"
    sudo ufw status | grep -q "80/tcp" || sudo ufw allow 80/tcp
    sudo ufw status | grep -q "443/tcp" || sudo ufw allow 443/tcp
    sudo systemctl restart nginx
fi

echo ""
echo -e "${BLUE}4. Проверка доступности...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -qE "200|301|302"; then
    echo -e "${GREEN}✓ Nginx отвечает на порту 80${NC}"
else
    echo -e "${RED}✗ Nginx не отвечает!${NC}"
    echo -e "${YELLOW}Проверьте логи: sudo tail -20 /var/log/nginx/error.log${NC}"
fi

echo ""
echo -e "${GREEN}✓ Проверка завершена${NC}"

