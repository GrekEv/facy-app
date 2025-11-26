#!/bin/bash
# Простой скрипт для запуска API на сервере

cd ~/facy-app || cd /home/ubuntu/facy-app || cd /root/facy-app || {
    echo "Директория не найдена!"
    exit 1
}

# Определяем команду docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE="docker compose"
else
    echo "Docker Compose не найден!"
    exit 1
fi

echo "Используется: $COMPOSE"
echo "Директория: $(pwd)"
echo ""

echo "Остановка старых контейнеров..."
$COMPOSE -f docker-compose.prod.yml down 2>/dev/null || true

echo "Запуск контейнеров..."
$COMPOSE -f docker-compose.prod.yml up -d

echo ""
echo "Ожидание запуска (20 секунд)..."
sleep 20

echo ""
echo "Статус контейнеров:"
$COMPOSE -f docker-compose.prod.yml ps

echo ""
echo "Проверка health:"
curl -s http://localhost:8000/health || echo "API не отвечает"

echo ""
echo "Готово!"

