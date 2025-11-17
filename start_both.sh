#!/bin/bash

# Скрипт для запуска API и бота вместе
# Использование: ./start_both.sh

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Запуск Telegram Mini App (API + Bot)${NC}"
echo ""

# Проверка переменных окружения
if [ -z "$BOT_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  BOT_TOKEN не установлен${NC}"
    echo "Установите переменную окружения:"
    echo "  export BOT_TOKEN=ваш_токен_бота"
    exit 1
fi

if [ -z "$WEBAPP_URL" ]; then
    echo -e "${YELLOW}⚠️  WEBAPP_URL не установлен${NC}"
    echo "Установите переменную окружения:"
    echo "  export WEBAPP_URL=https://your-app-url.com"
    exit 1
fi

# Проверка файла .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Файл .env не найден${NC}"
    echo "Создайте файл .env на основе ENV_EXAMPLE.txt"
    exit 1
fi

# Создание директорий
mkdir -p data uploads generated temp

# Функция очистки при выходе
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Остановка приложения...${NC}"
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    if [ ! -z "$BOT_PID" ]; then
        kill $BOT_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Запуск API в фоне
echo -e "${BLUE}📡 Запуск API сервера...${NC}"
python run_api.py > api.log 2>&1 &
API_PID=$!

# Ждем запуска API
echo -e "${BLUE}⏳ Ожидание запуска API (3 секунды)...${NC}"
sleep 3

# Проверка, что API запущен
if ! kill -0 $API_PID 2>/dev/null; then
    echo -e "${RED}❌ API не запустился! Проверьте api.log${NC}"
    exit 1
fi

echo -e "${GREEN}✅ API запущен на http://localhost:8000${NC}"

# Запуск бота
echo -e "${BLUE}🤖 Запуск Telegram бота...${NC}"
python main.py > bot.log 2>&1 &
BOT_PID=$!

# Ждем запуска бота
sleep 2

# Проверка, что бот запущен
if ! kill -0 $BOT_PID 2>/dev/null; then
    echo -e "${RED}❌ Бот не запустился! Проверьте bot.log${NC}"
    cleanup
    exit 1
fi

echo -e "${GREEN}✅ Бот запущен${NC}"
echo ""
echo -e "${GREEN}✅ Приложение работает!${NC}"
echo -e "${BLUE}📝 API: http://localhost:8000${NC}"
echo -e "${BLUE}📝 Web App: ${WEBAPP_URL}${NC}"
echo ""
echo -e "${YELLOW}⚠️  Для остановки нажмите Ctrl+C${NC}"
echo ""

# Ждем завершения
wait

