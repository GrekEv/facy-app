#!/bin/bash
# Полный скрипт для исправления всех проблем на сервере

set -e

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

echo "🔧 Исправление всех проблем..."

# 1. Исправляем config.py - добавляем ENVIRONMENT поле
if ! grep -q "ENVIRONMENT: str" config.py; then
    echo "  ✓ Добавляю поле ENVIRONMENT в config.py..."
    sed -i '/WEBAPP_URL: str/a\    \n    # Environment\n    ENVIRONMENT: str = "production"  # development, production' config.py
else
    echo "  ✓ Поле ENVIRONMENT уже существует"
fi

# 2. Добавляем extra = "ignore" в Config класс
if ! grep -q 'extra = "ignore"' config.py; then
    echo "  ✓ Добавляю extra = \"ignore\" в Config класс..."
    sed -i '/case_sensitive = True/a\        extra = "ignore"  # Игнорировать дополнительные поля из .env' config.py
else
    echo "  ✓ extra = \"ignore\" уже настроен"
fi

# 3. Исправляем импорты в api/main.py
echo "  ✓ Исправляю импорты в api/main.py..."
sed -i 's/from \.schemas import/from api.schemas import/g' api/main.py
sed -i 's/from \. import payments/from api import payments/g' api/main.py

# 4. Удаляем устаревший version из docker-compose.yml
if grep -q "^version:" docker-compose.yml; then
    echo "  ✓ Удаляю устаревший version из docker-compose.yml..."
    sed -i '/^version:/d' docker-compose.yml
else
    echo "  ✓ version уже удален"
fi

echo ""
echo "✅ Все файлы исправлены!"
echo ""
echo "🔄 Останавливаю контейнеры..."
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
docker compose down 2>/dev/null || true

echo ""
echo "🔨 Пересобираю образы..."
docker compose -f docker-compose.prod.yml build

echo ""
echo "🚀 Запускаю контейнеры..."
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Ожидание запуска (15 секунд)..."
sleep 15

echo ""
echo "📊 Статус контейнеров:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "📋 Последние логи API:"
docker compose -f docker-compose.prod.yml logs api --tail=30

echo ""
echo "✅ Готово!"
echo ""
echo "Проверка:"
echo "  - API Health: http://158.160.96.182:8000/health"
echo "  - Web App: http://158.160.96.182:8000"
echo ""
echo "Просмотр логов:"
echo "  docker compose -f docker-compose.prod.yml logs -f"

