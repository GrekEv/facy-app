#!/bin/bash

cd "$(dirname "$0")"

echo "�� О�танавл�ваем �та��й �е�ве�..."
pkill -f "uvicorn.*api.main" || true
pkill -f "python.*run_api" || true
sleep 2

echo " �а�т�ойка ок�ужен��..."
export BOT_TOKEN=${BOT_TOKEN:-test_token_123}
export WEBAPP_URL=${WEBAPP_URL:-http://localhost:8000}
export ENVIRONMENT=development
export HOST=127.0.0.1
export PORT=8000

# ��ове��ем нал�ч�е .env файла
if [ ! -f .env ]; then
    echo "  Файл .env не найден, ��пол�зуем значен�� по умолчан��"
fi

echo " Запу�к локал�но�о �е�ве�а на http://127.0.0.1:8000"
echo " Ло�� �удут ото��ажат��� н�же..."
echo ""

# �оздаем д��екто��� е�л� �� нет
mkdir -p data uploads generated temp

# Запу�каем �е�ве�
python3 run_api.py


