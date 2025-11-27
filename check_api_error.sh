#!/bin/bash
# Диагностика ошибки контейнера facy-api

cd ~/facy-app 2>/dev/null || cd /home/ubuntu/facy-app 2>/dev/null || cd /root/facy-app 2>/dev/null || {
    echo "✗ Директория ~/facy-app не найдена!"
    exit 1
}

# Определяем команду docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE="docker compose"
else
    echo "✗ Docker Compose не найден!"
    exit 1
fi

echo "=========================================="
echo "ДИАГНОСТИКА ОШИБКИ API"
echo "=========================================="
echo ""

echo "1. Статус контейнеров:"
$COMPOSE -f docker-compose.prod.yml ps
echo ""

echo "2. Логи API (последние 50 строк):"
$COMPOSE -f docker-compose.prod.yml logs --tail=50 api
echo ""

echo "3. Логи всех контейнеров:"
$COMPOSE -f docker-compose.prod.yml logs --tail=30
echo ""

echo "4. Проверка .env файла:"
if [ -f .env ]; then
    echo "  ✓ .env файл существует"
    echo ""
    echo "  Проверка обязательных переменных:"
    if grep -q "BOT_TOKEN=" .env; then
        BOT_TOKEN=$(grep "BOT_TOKEN=" .env | cut -d'=' -f2)
        if [ -n "$BOT_TOKEN" ] && [ "$BOT_TOKEN" != "" ]; then
            echo "    ✓ BOT_TOKEN установлен"
        else
            echo "    ✗ BOT_TOKEN пустой!"
        fi
    else
        echo "    ✗ BOT_TOKEN не найден в .env"
    fi
    
    if grep -q "WEBAPP_URL=" .env; then
        WEBAPP_URL=$(grep "WEBAPP_URL=" .env | cut -d'=' -f2)
        echo "    ✓ WEBAPP_URL: $WEBAPP_URL"
    else
        echo "    ⚠ WEBAPP_URL не установлен (будет определен автоматически)"
    fi
    
    if grep -q "DATABASE_URL=" .env; then
        echo "    ✓ DATABASE_URL установлен"
    else
        echo "    ⚠ DATABASE_URL не установлен (будет использован SQLite)"
    fi
else
    echo "  ✗ .env файл не найден!"
    echo "  Создайте .env файл с необходимыми переменными"
fi
echo ""

echo "5. Проверка Docker:"
docker ps -a | grep facy-api
echo ""

echo "6. Попытка перезапуска:"
echo "  Выполните:"
echo "    $COMPOSE -f docker-compose.prod.yml restart api"
echo ""

echo "7. Если не помогает, пересоберите:"
echo "    $COMPOSE -f docker-compose.prod.yml down"
echo "    $COMPOSE -f docker-compose.prod.yml up -d --build"
echo ""

