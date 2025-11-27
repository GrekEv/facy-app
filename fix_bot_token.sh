#!/bin/bash
# Добавление BOT_TOKEN в .env файл

cd ~/facy-app 2>/dev/null || cd /home/ubuntu/facy-app 2>/dev/null || cd /root/facy-app 2>/dev/null || {
    echo "✗ Директория ~/facy-app не найдена!"
    exit 1
}

echo "=========================================="
echo "ДОБАВЛЕНИЕ BOT_TOKEN"
echo "=========================================="
echo ""

# Проверка существования .env
if [ ! -f .env ]; then
    echo "Создание .env файла..."
    touch .env
fi

# Проверка, есть ли уже BOT_TOKEN
if grep -q "^BOT_TOKEN=" .env; then
    echo "⚠ BOT_TOKEN уже существует в .env"
    echo ""
    echo "Текущее значение:"
    grep "^BOT_TOKEN=" .env | sed 's/BOT_TOKEN=\(.*\)/BOT_TOKEN=***скрыто***/'
    echo ""
    read -p "Заменить? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Отменено"
        exit 0
    fi
    # Удаляем старую строку
    sed -i '/^BOT_TOKEN=/d' .env
fi

echo ""
echo "Введите BOT_TOKEN от BotFather:"
echo "  (Получите токен: https://t.me/BotFather -> /newbot или /token)"
echo ""
read -p "BOT_TOKEN: " BOT_TOKEN

if [ -z "$BOT_TOKEN" ]; then
    echo "✗ BOT_TOKEN не может быть пустым!"
    exit 1
fi

# Добавляем BOT_TOKEN в начало файла
echo "BOT_TOKEN=$BOT_TOKEN" >> .env

echo ""
echo "✓ BOT_TOKEN добавлен в .env"
echo ""

# Проверяем другие обязательные переменные
if ! grep -q "^WEBAPP_URL=" .env; then
    echo "Добавление WEBAPP_URL..."
    echo "WEBAPP_URL=https://onlyface.art" >> .env
    echo "✓ WEBAPP_URL добавлен"
fi

echo ""
echo "Содержимое .env (без секретов):"
grep -v -E "(TOKEN|KEY|PASSWORD|SECRET)" .env | head -10
echo ""

echo "=========================================="
echo "ПЕРЕЗАПУСК КОНТЕЙНЕРОВ"
echo "=========================================="
echo ""

# Определяем команду docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE="docker compose"
else
    echo "✗ Docker Compose не найден!"
    exit 1
fi

echo "Остановка контейнеров..."
$COMPOSE -f docker-compose.prod.yml down

echo ""
echo "Запуск контейнеров..."
$COMPOSE -f docker-compose.prod.yml up -d

echo ""
echo "Ожидание запуска (30 секунд)..."
sleep 30

echo ""
echo "Проверка статуса:"
$COMPOSE -f docker-compose.prod.yml ps

echo ""
echo "Проверка health:"
curl -s http://localhost:8000/health | head -5 || echo "API еще запускается..."

echo ""
echo "=========================================="
echo "✓ ГОТОВО!"
echo "=========================================="
echo ""
echo "Проверьте домен:"
echo "  curl https://onlyface.art/health"
echo ""

