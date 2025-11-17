#!/bin/bash

cd "$(dirname "$0")"

echo "🛑 Останавливаем старый сервер..."
pkill -f "uvicorn.*api.main" || true
pkill -f "python.*run_api" || true
sleep 2

echo "🔧 Настройка окружения..."
export BOT_TOKEN=${BOT_TOKEN:-test_token_123}
export WEBAPP_URL=${WEBAPP_URL:-http://localhost:8000}
export ENVIRONMENT=development
export HOST=127.0.0.1
export PORT=8000

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден, используем значения по умолчанию"
fi

echo "🚀 Запуск локального сервера на http://127.0.0.1:8000"
echo "📝 Логи будут отображаться ниже..."
echo ""

# Создаем директории если их нет
mkdir -p data uploads generated temp

# Запускаем сервер
python3 run_api.py


