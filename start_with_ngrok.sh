#!/bin/bash

# Скрипт для запуска приложения с ngrok туннелем
# Использование: ./start_with_ngrok.sh

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Запуск Telegram Mini App с ngrok${NC}"
echo ""

# Проверка наличия ngrok
if ! command -v ngrok &> /dev/null; then
    echo -e "${RED}❌ ngrok не установлен!${NC}"
    echo ""
    echo "Установите ngrok:"
    echo "  macOS: brew install ngrok"
    echo "  Linux: wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
    echo "  Windows: https://ngrok.com/download"
    echo ""
    echo "Зарегистрируйтесь на https://ngrok.com и получите токен"
    echo "Затем выполните: ngrok config add-authtoken ваш_токен"
    exit 1
fi

# Проверка наличия Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python не установлен!${NC}"
    exit 1
fi

# Проверка переменных окружения
if [ -z "$BOT_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  BOT_TOKEN не установлен${NC}"
    echo "Установите переменную окружения:"
    echo "  export BOT_TOKEN=ваш_токен_бота"
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
    if [ ! -z "$NGROK_PID" ]; then
        kill $NGROK_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Запуск API в фоне
echo -e "${BLUE}📡 Запуск API сервера...${NC}"
python run_api.py > api.log 2>&1 &
API_PID=$!

# Ждем запуска API
echo -e "${BLUE}⏳ Ожидание запуска API (5 секунд)...${NC}"
sleep 5

# Проверка, что API запущен
if ! kill -0 $API_PID 2>/dev/null; then
    echo -e "${RED}❌ API не запустился! Проверьте api.log${NC}"
    exit 1
fi

# Запуск ngrok
echo -e "${BLUE}🌐 Запуск ngrok туннеля...${NC}"
ngrok http 8000 --log=stdout > ngrok.log 2>&1 &
NGROK_PID=$!

# Ждем запуска ngrok
echo -e "${BLUE}⏳ Ожидание запуска ngrok (5 секунд)...${NC}"
sleep 5

# Получение URL из ngrok API
echo -e "${BLUE}🔍 Получение ngrok URL...${NC}"
MAX_RETRIES=10
RETRY_COUNT=0
NGROK_URL=""

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o 'https://[^"]*\.ngrok-free\.app' | head -1 || echo "")
    
    if [ ! -z "$NGROK_URL" ]; then
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 2
done

if [ -z "$NGROK_URL" ]; then
    echo -e "${RED}❌ Не удалось получить ngrok URL!${NC}"
    echo "Проверьте ngrok.log"
    cleanup
    exit 1
fi

echo ""
echo -e "${GREEN}✅ API запущен на http://localhost:8000${NC}"
echo -e "${GREEN}✅ ngrok туннель: ${NGROK_URL}${NC}"
echo ""
echo -e "${YELLOW}📝 ВАЖНО: Обновите WEBAPP_URL в BotFather:${NC}"
echo -e "${BLUE}   1. Откройте @BotFather в Telegram${NC}"
echo -e "${BLUE}   2. /mybots → выберите бота${NC}"
echo -e "${BLUE}   3. Bot Settings → Menu Button${NC}"
echo -e "${BLUE}   4. URL: ${NGROK_URL}${NC}"
echo ""
echo -e "${YELLOW}📝 Также обновите WEBAPP_URL в переменных окружения:${NC}"
echo -e "${BLUE}   export WEBAPP_URL=${NGROK_URL}${NC}"
echo ""

# Установка WEBAPP_URL для бота
export WEBAPP_URL=$NGROK_URL

# Запуск бота
echo -e "${BLUE}🤖 Запуск Telegram бота...${NC}"
echo -e "${YELLOW}⚠️  Для остановки нажмите Ctrl+C${NC}"
echo ""

python main.py

# Очистка при выходе
cleanup

