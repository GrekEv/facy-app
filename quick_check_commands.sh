#!/bin/bash
# Команды для быстрой проверки (выполнить на сервере)

echo "=== БЫСТРАЯ ПРОВЕРКА ==="
echo ""

echo "1. СЕРВЕР:"
uptime
echo ""

echo "2. DOCKER:"
docker compose -f docker-compose.prod.yml ps
echo ""

echo "3. ПРИЛОЖЕНИЕ:"
curl -s http://localhost:8000/health
echo ""
curl -s http://localhost:8000/api/health | head -3
echo ""

echo "4. NGINX:"
sudo systemctl is-active nginx && echo "✓ Nginx работает" || echo "✗ Nginx не работает"
curl -s -o /dev/null -w "HTTP статус: %{http_code}\n" http://localhost/
echo ""

echo "5. БД (из health check):"
curl -s http://localhost:8000/api/health | grep -o '"database"[^}]*}' || echo "Проверьте ответ выше"
echo ""

echo "6. FIREWALL:"
sudo ufw status | head -5
echo ""

echo "7. ПОРТЫ:"
sudo ss -tlnp 2>/dev/null | grep -E ':(80|8000)' || sudo netstat -tlnp 2>/dev/null | grep -E ':(80|8000)' || echo "Порты не найдены"
echo ""

echo "8. ДОМЕН:"
dig +short onlyface.art 2>/dev/null | tail -1 || echo "DNS не резолвится"
echo ""

echo "=== ГОТОВО ==="

