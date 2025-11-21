#!/bin/bash
# Скрипт для проверки статуса сайта

echo "=== ПРОВЕРКА СТАТУСА САЙТА ==="
echo ""

echo "1. Проверка Docker контейнеров:"
docker compose -f docker-compose.prod.yml ps
echo ""

echo "2. Проверка приложения (порт 8000):"
curl -s http://localhost:8000/health | head -1
echo ""

echo "3. Проверка через Nginx (порт 80):"
curl -s -o /dev/null -w "HTTP статус: %{http_code}\n" http://localhost/
echo ""

echo "4. Проверка портов:"
sudo netstat -tlnp 2>/dev/null | grep -E ':(80|8000)' || echo "Порты не найдены"
echo ""

echo "5. Статус Nginx:"
sudo systemctl is-active nginx && echo "✓ Nginx работает" || echo "✗ Nginx не работает"
echo ""

echo "=== ГОТОВО ==="

