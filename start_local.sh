#!/bin/bash
cd "$(dirname "$0")"
export BOT_TOKEN=test_token_123
export WEBAPP_URL=http://localhost:8000
export ENVIRONMENT=development
export HOST=127.0.0.1
export PORT=8000

mkdir -p data

echo "🚀 Запуск сервера на http://127.0.0.1:8000"
python3 -m uvicorn api.main:app --host 127.0.0.1 --port 8000


