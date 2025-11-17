#!/bin/bash
# Полный скрипт для исправления всех проблем на сервере

set -e

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

echo "🔧 Исправление всех проблем..."

# 1. Исправляем config.py - добавляем ENVIRONMENT поле
if ! grep -q "ENVIRONMENT: str" config.py; then
    echo "  ✓ Добавляю поле ENVIRONMENT в config.py..."
    sed -i '/WEBAPP_URL: str/a\    \n    # Environment\n    ENVIRONMENT: str = "production"  # development, production' config.py
fi

# 2. Добавляем extra = "ignore" в Config класс
if ! grep -q 'extra = "ignore"' config.py; then
    echo "  ✓ Добавляю extra = \"ignore\" в Config класс..."
    sed -i '/case_sensitive = True/a\        extra = "ignore"  # Игнорировать дополнительные поля из .env' config.py
fi

# 3. Исправляем импорты в api/main.py
echo "  ✓ Исправляю импорты в api/main.py..."
sed -i 's/from \.schemas import/from api.schemas import/g' api/main.py
sed -i 's/from \. import payments/from api import payments/g' api/main.py

# 4. Удаляем устаревший version из docker-compose.yml
if grep -q "^version:" docker-compose.yml; then
    echo "  ✓ Удаляю устаревший version из docker-compose.yml..."
    sed -i '/^version:/d' docker-compose.yml
fi

# 5. Исправляем models.py - обновляем Base на DeclarativeBase
echo "  ✓ Обновляю Base на DeclarativeBase в models.py..."
sed -i 's/from sqlalchemy.ext.declarative import declarative_base/from sqlalchemy.orm import DeclarativeBase, relationship/g' database/models.py
sed -i 's/^Base = declarative_base()$/class Base(DeclarativeBase):\n    """Базовый класс для всех моделей"""\n    pass/g' database/models.py

# 6. КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Заменяем metadata на transaction_metadata
echo "  ✓ Исправляю metadata на transaction_metadata в Transaction классе..."
sed -i 's/^    metadata = Column(Text, nullable=True)/    transaction_metadata = Column(Text, nullable=True)/g' database/models.py

# 7. Обновляем healthcheck в docker-compose.prod.yml
echo "  ✓ Обновляю healthcheck..."
if ! grep -q "start_period" docker-compose.prod.yml; then
    sed -i '/retries: 3$/a\      start_period: 40s' docker-compose.prod.yml
    sed -i 's/retries: 3/retries: 5/g' docker-compose.prod.yml
fi

echo ""
echo "✅ Все файлы исправлены!"
echo ""
echo "🔄 Останавливаю контейнеры..."
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
docker compose down 2>/dev/null || true

echo ""
echo "🔨 Пересобираю образы..."
docker compose -f docker-compose.prod.yml build --no-cache

echo ""
echo "🚀 Запускаю контейнеры..."
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Ожидание запуска (25 секунд)..."
sleep 25

echo ""
echo "📊 Статус контейнеров:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "📋 Последние логи API:"
docker compose -f docker-compose.prod.yml logs api --tail=40

echo ""
echo "📋 Последние логи Bot:"
docker compose -f docker-compose.prod.yml logs bot --tail=20

echo ""
echo "🔍 Проверка health endpoint:"
sleep 5
curl -f http://localhost:8000/health 2>/dev/null && echo "✅ API работает!" || echo "⚠️ API еще запускается..."

echo ""
echo "✅ Готово!"
echo ""
echo "Проверка:"
echo "  - API Health: http://158.160.96.182:8000/health"
echo "  - Web App: http://158.160.96.182:8000"
echo ""
echo "Просмотр логов:"
echo "  docker compose -f docker-compose.prod.yml logs -f"

