#!/bin/bash
# Полная проверка системы

echo "=== ПОЛНАЯ ПРОВЕРКА СИСТЕМЫ ==="
echo ""

echo "1. ПРИЛОЖЕНИЕ:"
curl -s http://localhost:8000/health && echo ""
echo ""
echo "2. API HEALTH (с БД):"
curl -s http://localhost:8000/api/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/health
echo ""
echo "3. FIREWALL:"
sudo ufw status
echo ""
echo "4. ПОРТЫ:"
sudo ss -tlnp 2>/dev/null | grep -E ':(80|8000)' || echo "Порты не найдены"
echo ""
echo "5. ДОМЕН (DNS):"
DOMAIN_IP=$(dig +short onlyface.art 2>/dev/null | tail -1)
if [ -n "$DOMAIN_IP" ]; then
    echo "  DNS: onlyface.art -> $DOMAIN_IP"
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "158.160.96.182")
    if [ "$DOMAIN_IP" = "$SERVER_IP" ] || [ "$DOMAIN_IP" = "158.160.96.182" ]; then
        echo "  ✓ DNS настроен правильно"
    else
        echo "  ⚠ DNS может указывать не на этот сервер"
    fi
else
    echo "  ✗ Домен не резолвится"
fi
echo ""
echo "6. NGINX:"
sudo systemctl is-active nginx && echo "  ✓ Nginx работает" || echo "  ✗ Nginx не работает"
NGINX_HTTP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null)
echo "  HTTP статус: $NGINX_HTTP"
echo ""
echo "7. DOCKER:"
docker compose -f docker-compose.prod.yml ps
echo ""
echo "=== ГОТОВО ==="

