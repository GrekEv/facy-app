#!/bin/bash
# Автоматический запуск приложения Facy

set -e

cd ~/facy-app

echo "🔍 Проверка .env файла..."
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден! Создаю..."
    cat > .env << 'ENVEOF'
# ОБЯЗАТЕЛЬНЫЕ ПЕРЕМЕННЫЕ
BOT_TOKEN=your_bot_token_here
WEBAPP_URL=http://158.160.96.182:8000
ENVIRONMENT=production
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
HOST=0.0.0.0
PORT=8000

# ============================================
# API КЛЮЧИ ДЛЯ ГЕНЕРАЦИИ ИЗОБРАЖЕНИЙ
# ============================================

# Replicate (рекомендуется для изображений)
REPLICATE_API_KEY=your_replicate_api_key_here
REPLICATE_API_URL=https://api.replicate.com/v1

# ============================================
# API КЛЮЧИ ДЛЯ ГЕНЕРАЦИИ ВИДЕО
# ============================================

# OpenAI Sora (для генерации видео)
OPENAI_API_KEY=your_openai_api_key_here
SORA_MODEL=sora-1.0-pro

# Higgsfield.ai (опционально)
HIGGSFIELD_API_KEY=
HIGGSFIELD_API_URL=https://api.higgsfield.ai

# ============================================
# ВЫБОР ПРОВАЙДЕРОВ
# ============================================

# Для генерации изображений
IMAGE_GENERATION_PROVIDER=replicate

# Для генерации видео
VIDEO_GENERATION_PROVIDER=sora
ENVEOF
    echo "✅ Файл .env создан!"
fi

echo ""
echo "🔨 Сборка Docker образов..."
docker-compose -f docker-compose.prod.yml build

echo ""
echo "🚀 Запуск приложения..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Ожидание запуска (15 секунд)..."
sleep 15

echo ""
echo "📊 Статус контейнеров:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🔍 Проверка API..."
sleep 5
curl -f http://localhost:8000/health && echo "✅ API работает!" || echo "⚠️ API еще запускается..."

echo ""
echo "✅ Готово! Приложение запущено."
echo ""
echo "Проверка:"
echo "  - API: http://158.160.96.182:8000/health"
echo "  - Web App: http://158.160.96.182:8000"
echo ""
echo "Логи:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"

