#!/bin/bash
# Полная проверка сервера: БД, API, фронтенд, бэкенд

cd ~/facy-app 2>/dev/null || {
    echo "✗ Директория ~/facy-app не найдена!"
    exit 1
}

echo "=========================================="
echo "ПОЛНАЯ ПРОВЕРКА СЕРВЕРА"
echo "=========================================="
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
    exit 1
fi

echo ""
echo "1. ПРОВЕРКА КОНТЕЙНЕРОВ:"
echo "------------------------"
$COMPOSE -f docker-compose.prod.yml ps
echo ""

echo "2. ПРОВЕРКА ЛОГОВ API:"
echo "------------------------"
$COMPOSE -f docker-compose.prod.yml logs api --tail=30
echo ""

echo "3. ПРОВЕРКА ПОДКЛЮЧЕНИЯ К БД:"
echo "------------------------"
# Проверяем DATABASE_URL
if [ -f .env ]; then
    DB_URL=$(grep "^DATABASE_URL=" .env | cut -d'=' -f2- | sed 's/:[^:@]*@/:***@/')
    if [ -n "$DB_URL" ]; then
        echo "  ✓ DATABASE_URL установлен: $DB_URL"
    else
        echo "  ✗ DATABASE_URL не найден в .env"
    fi
else
    echo "  ✗ .env файл не найден"
fi
echo ""

echo "4. ПРОВЕРКА API (localhost:8000):"
echo "------------------------"
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ -n "$HEALTH" ]; then
    echo "  ✓ API отвечает:"
    echo "$HEALTH" | head -10
    echo ""
    # Проверка подключения к БД через API
    API_HEALTH=$(curl -s http://localhost:8000/api/health 2>/dev/null)
    if [ -n "$API_HEALTH" ]; then
        echo "  ✓ API health endpoint:"
        echo "$API_HEALTH" | head -10
        # Проверяем наличие информации о БД
        if echo "$API_HEALTH" | grep -qi "database"; then
            echo ""
            echo "  ✓ Информация о БД в ответе API"
        fi
    fi
else
    echo "  ✗ API не отвечает на localhost:8000"
    echo "  Возможные причины:"
    echo "    - Контейнер не запущен"
    echo "    - Ошибка в логах"
    echo "    - Порт 8000 не слушается"
fi
echo ""

echo "5. ПРОВЕРКА ФАЙЛОВ ФРОНТЕНДА:"
echo "------------------------"
if [ -d "templates" ] && [ -f "templates/index.html" ]; then
    echo "  ✓ templates/index.html существует"
    echo "    Размер: $(stat -f%z templates/index.html 2>/dev/null || stat -c%s templates/index.html 2>/dev/null) байт"
else
    echo "  ✗ templates/index.html не найден"
fi

if [ -d "static" ]; then
    echo "  ✓ Директория static существует"
    if [ -d "static/js" ] && [ -f "static/js/app.js" ]; then
        echo "    ✓ static/js/app.js существует"
    fi
    if [ -d "static/css" ] && [ -f "static/css/style.css" ]; then
        echo "    ✓ static/css/style.css существует"
    fi
else
    echo "  ✗ Директория static не найдена"
fi
echo ""

echo "6. ПРОВЕРКА ФАЙЛОВ БЭКЕНДА:"
echo "------------------------"
if [ -d "api" ] && [ -f "api/main.py" ]; then
    echo "  ✓ api/main.py существует"
    echo "    Размер: $(stat -f%z api/main.py 2>/dev/null || stat -c%s api/main.py 2>/dev/null) байт"
else
    echo "  ✗ api/main.py не найден"
fi

if [ -f "run_api.py" ]; then
    echo "  ✓ run_api.py существует"
fi

if [ -f "config.py" ]; then
    echo "  ✓ config.py существует"
fi
echo ""

echo "7. ПРОВЕРКА ПОРТА 8000:"
echo "------------------------"
if netstat -tlnp 2>/dev/null | grep -q ":8000"; then
    echo "  ✓ Порт 8000 слушается"
    netstat -tlnp 2>/dev/null | grep ":8000"
elif ss -tlnp 2>/dev/null | grep -q ":8000"; then
    echo "  ✓ Порт 8000 слушается"
    ss -tlnp 2>/dev/null | grep ":8000"
else
    echo "  ✗ Порт 8000 не слушается"
fi
echo ""

echo "8. ПРОВЕРКА ЧЕРЕЗ ДОМЕН:"
echo "------------------------"
DOMAIN_HEALTH=$(curl -s https://onlyface.art/health 2>/dev/null)
if [ -n "$DOMAIN_HEALTH" ] && ! echo "$DOMAIN_HEALTH" | grep -q "502"; then
    echo "  ✓ Домен отвечает:"
    echo "$DOMAIN_HEALTH" | head -5
else
    echo "  ✗ Домен возвращает 502 или не отвечает"
    echo "    Это нормально, если API не запущен"
fi
echo ""

echo "=========================================="
echo "РЕКОМЕНДАЦИИ:"
echo "=========================================="
echo ""

# Проверяем статус контейнеров
CONTAINERS=$($COMPOSE -f docker-compose.prod.yml ps -q 2>/dev/null)
if [ -z "$CONTAINERS" ]; then
    echo "⚠ Контейнеры не запущены!"
    echo "  Запустите: $COMPOSE -f docker-compose.prod.yml up -d"
elif ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠ API не отвечает, но контейнеры запущены"
    echo "  Проверьте логи: $COMPOSE -f docker-compose.prod.yml logs api"
    echo "  Перезапустите: $COMPOSE -f docker-compose.prod.yml restart api"
else
    echo "✓ Всё работает!"
fi
echo ""

