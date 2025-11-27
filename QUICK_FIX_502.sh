#!/bin/bash
# Быстрое исправление 502 Bad Gateway - запуск API на сервере

echo "=========================================="
echo "ЗАПУСК API ДЛЯ onlyface.art"
echo "=========================================="
echo ""

# Переход в директорию проекта
cd ~/facy-app 2>/dev/null || cd /home/ubuntu/facy-app 2>/dev/null || cd /root/facy-app 2>/dev/null || {
    echo "✗ Директория ~/facy-app не найдена!"
    echo "  Создайте директорию или склонируйте репозиторий:"
    echo "  git clone https://github.com/GrekEv/facy-app.git ~/facy-app"
    exit 1
}

echo "✓ Директория: $(pwd)"
echo ""

# Определяем команду docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
    echo "✓ Используется: docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE="docker compose"
    echo "✓ Используется: docker compose"
else
    echo "✗ Docker Compose не найден!"
    echo "  Установите Docker Compose"
    exit 1
fi

echo ""
echo "1. Проверка .env файла..."
if [ ! -f .env ]; then
    echo "  ⚠ .env файл не найден!"
    echo "  Создайте .env файл с необходимыми переменными"
else
    echo "  ✓ .env файл найден"
    if ! grep -q "BOT_TOKEN=" .env; then
        echo "  ⚠ BOT_TOKEN не установлен в .env"
    fi
fi

echo ""
echo "2. Остановка старых контейнеров..."
$COMPOSE -f docker-compose.prod.yml down 2>/dev/null || true

echo ""
echo "3. Запуск контейнеров..."
$COMPOSE -f docker-compose.prod.yml up -d

if [ $? -ne 0 ]; then
    echo "✗ Ошибка при запуске контейнеров!"
    echo ""
    echo "Проверьте логи:"
    echo "  $COMPOSE -f docker-compose.prod.yml logs"
    exit 1
fi

echo ""
echo "4. Ожидание запуска API (30 секунд)..."
sleep 30

echo ""
echo "5. Проверка статуса контейнеров:"
$COMPOSE -f docker-compose.prod.yml ps

echo ""
echo "6. Проверка health endpoint:"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ -n "$HEALTH_RESPONSE" ]; then
    echo "  ✓ API отвечает:"
    echo "$HEALTH_RESPONSE" | head -5
else
    echo "  ✗ API не отвечает на localhost:8000"
    echo ""
    echo "Проверьте логи:"
    echo "  $COMPOSE -f docker-compose.prod.yml logs api"
    echo ""
    echo "Проверьте порт:"
    echo "  netstat -tlnp | grep 8000"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ API ЗАПУЩЕН"
echo "=========================================="
echo ""
echo "Проверьте домен:"
echo "  curl https://onlyface.art/health"
echo ""

