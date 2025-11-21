#!/bin/bash
# Полная проверка статуса сервера, БД, домена и firewall

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== ПОЛНАЯ ПРОВЕРКА СИСТЕМЫ ===${NC}"
echo ""

# 1. СЕРВЕР
echo -e "${BLUE}1. СЕРВЕР:${NC}"
echo -n "  Hostname: "
hostname
echo -n "  Uptime: "
uptime -p 2>/dev/null || uptime
echo -n "  Load: "
uptime | awk -F'load average:' '{print $2}'
echo ""

# 2. DOCKER КОНТЕЙНЕРЫ
echo -e "${BLUE}2. DOCKER КОНТЕЙНЕРЫ:${NC}"
docker compose -f docker-compose.prod.yml ps
echo ""

# 3. ПРИЛОЖЕНИЕ
echo -e "${BLUE}3. ПРИЛОЖЕНИЕ (порт 8000):${NC}"
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ -n "$HEALTH" ]; then
    echo -e "  ${GREEN}✓ Приложение работает${NC}"
    echo "  Ответ: $HEALTH"
else
    echo -e "  ${RED}✗ Приложение не отвечает${NC}"
fi
echo ""

# 4. NGINX
echo -e "${BLUE}4. NGINX (порт 80):${NC}"
if sudo systemctl is-active --quiet nginx; then
    echo -e "  ${GREEN}✓ Nginx работает${NC}"
    NGINX_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null)
    if [ "$NGINX_STATUS" = "200" ]; then
        echo -e "  ${GREEN}✓ Nginx отвечает (HTTP $NGINX_STATUS)${NC}"
    else
        echo -e "  ${YELLOW}⚠ Nginx отвечает, но статус: $NGINX_STATUS${NC}"
    fi
else
    echo -e "  ${RED}✗ Nginx не работает${NC}"
fi
echo ""

# 5. БАЗА ДАННЫХ
echo -e "${BLUE}5. БАЗА ДАННЫХ:${NC}"
DB_HEALTH=$(curl -s http://localhost:8000/api/health 2>/dev/null | grep -o '"database"[^}]*}' || echo "")
if echo "$DB_HEALTH" | grep -q "connected"; then
    echo -e "  ${GREEN}✓ База данных подключена${NC}"
elif echo "$DB_HEALTH" | grep -q "error"; then
    echo -e "  ${RED}✗ Ошибка подключения к БД${NC}"
    echo "  $DB_HEALTH"
else
    echo -e "  ${YELLOW}⚠ Статус БД неизвестен${NC}"
fi
echo ""

# 6. ПОРТЫ
echo -e "${BLUE}6. ОТКРЫТЫЕ ПОРТЫ:${NC}"
if command -v ss &> /dev/null; then
    echo "  Порт 80:"
    sudo ss -tlnp | grep ":80 " || echo "    Не найден"
    echo "  Порт 8000:"
    sudo ss -tlnp | grep ":8000 " || echo "    Не найден"
elif command -v netstat &> /dev/null; then
    echo "  Порт 80:"
    sudo netstat -tlnp 2>/dev/null | grep ":80 " || echo "    Не найден"
    echo "  Порт 8000:"
    sudo netstat -tlnp 2>/dev/null | grep ":8000 " || echo "    Не найден"
else
    echo "  Команды ss и netstat не найдены"
fi
echo ""

# 7. FIREWALL
echo -e "${BLUE}7. FIREWALL (UFW):${NC}"
if command -v ufw &> /dev/null; then
    UFW_STATUS=$(sudo ufw status 2>/dev/null | head -1)
    echo "  Статус: $UFW_STATUS"
    if echo "$UFW_STATUS" | grep -q "inactive"; then
        echo -e "  ${YELLOW}⚠ Firewall выключен${NC}"
    else
        echo "  Правила для портов 80, 443, 8000:"
        sudo ufw status | grep -E "(80|443|8000)" || echo "    Не найдены"
    fi
else
    echo -e "  ${YELLOW}⚠ UFW не установлен${NC}"
fi
echo ""

# 8. ДОМЕН
echo -e "${BLUE}8. ДОМЕН (onlyface.art):${NC}"
DOMAIN_IP=$(dig +short onlyface.art 2>/dev/null | tail -1)
if [ -n "$DOMAIN_IP" ]; then
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "не определен")
    echo "  DNS указывает на: $DOMAIN_IP"
    echo "  IP сервера: $SERVER_IP"
    if [ "$DOMAIN_IP" = "$SERVER_IP" ] || [ "$DOMAIN_IP" = "158.160.96.182" ]; then
        echo -e "  ${GREEN}✓ DNS настроен правильно${NC}"
    else
        echo -e "  ${YELLOW}⚠ DNS может указывать не на этот сервер${NC}"
    fi
else
    echo -e "  ${RED}✗ Домен не резолвится${NC}"
fi
echo ""

# 9. ВНЕШНЯЯ ДОСТУПНОСТЬ
echo -e "${BLUE}9. ВНЕШНЯЯ ДОСТУПНОСТЬ:${NC}"
EXTERNAL_HTTP=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://onlyface.art/ 2>/dev/null || echo "timeout")
if [ "$EXTERNAL_HTTP" = "200" ] || [ "$EXTERNAL_HTTP" = "301" ] || [ "$EXTERNAL_HTTP" = "302" ]; then
    echo -e "  ${GREEN}✓ Домен доступен извне (HTTP $EXTERNAL_HTTP)${NC}"
else
    echo -e "  ${YELLOW}⚠ Домен недоступен или возвращает: $EXTERNAL_HTTP${NC}"
fi
echo ""

# 10. РЕКОМЕНДАЦИИ ПО FIREWALL
echo -e "${BLUE}10. РЕКОМЕНДАЦИИ ПО FIREWALL:${NC}"
if command -v ufw &> /dev/null; then
    if sudo ufw status | grep -q "inactive"; then
        echo -e "  ${YELLOW}Firewall выключен. Рекомендуется включить:${NC}"
        echo "    sudo ufw allow 22/tcp    # SSH"
        echo "    sudo ufw allow 80/tcp   # HTTP"
        echo "    sudo ufw allow 443/tcp  # HTTPS"
        echo "    sudo ufw enable"
    else
        echo -e "  ${GREEN}Firewall активен${NC}"
        echo "  Проверьте правила выше"
    fi
else
    echo -e "  ${YELLOW}UFW не установлен. Установите:${NC}"
    echo "    sudo apt install ufw"
fi
echo ""

echo -e "${GREEN}=== ПРОВЕРКА ЗАВЕРШЕНА ===${NC}"

