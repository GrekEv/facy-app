#!/bin/bash

# �к��пт дл� запу�ка API � �ота вме�те
# И�пол�зован�е: ./start_both.sh

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE} Запу�к Telegram Mini App (API + Bot)${NC}"
echo ""

# ��ове�ка пе�еменн�� ок�ужен��
if [ -z "$BOT_TOKEN" ]; then
    echo -e "${YELLOW}  BOT_TOKEN не у�тановлен${NC}"
    echo "У�танов�те пе�еменну� ок�ужен��:"
    echo "  export BOT_TOKEN=ваш_токен_�ота"
    exit 1
fi

if [ -z "$WEBAPP_URL" ]; then
    echo -e "${YELLOW}  WEBAPP_URL не у�тановлен${NC}"
    echo "У�танов�те пе�еменну� ок�ужен��:"
    echo "  export WEBAPP_URL=https://your-app-url.com"
    exit 1
fi

# ��ове�ка файла .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}  Файл .env не найден${NC}"
    echo "�оздайте файл .env на о�нове ENV_EXAMPLE.txt"
    exit 1
fi

# �оздан�е д��екто��й
mkdir -p data uploads generated temp

# Функц�� оч��тк� п�� в��оде
cleanup() {
    echo ""
    echo -e "${YELLOW}�� О�тановка п��ложен��...${NC}"
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    if [ ! -z "$BOT_PID" ]; then
        kill $BOT_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Запу�к API в фоне
echo -e "${BLUE} Запу�к API �е�ве�а...${NC}"
python run_api.py > api.log 2>&1 &
API_PID=$!

# Ждем запу�ка API
echo -e "${BLUE} Ож�дан�е запу�ка API (3 �екунд�)...${NC}"
sleep 3

# ��ове�ка, что API запу�ен
if ! kill -0 $API_PID 2>/dev/null; then
    echo -e "${RED} API не запу�т�л��! ��ове��те api.log${NC}"
    exit 1
fi

echo -e "${GREEN} API запу�ен на http://localhost:8000${NC}"

# Запу�к �ота
echo -e "${BLUE}�� Запу�к Telegram �ота...${NC}"
python main.py > bot.log 2>&1 &
BOT_PID=$!

# Ждем запу�ка �ота
sleep 2

# ��ове�ка, что �от запу�ен
if ! kill -0 $BOT_PID 2>/dev/null; then
    echo -e "${RED} Бот не запу�т�л��! ��ове��те bot.log${NC}"
    cleanup
    exit 1
fi

echo -e "${GREEN} Бот запу�ен${NC}"
echo ""
echo -e "${GREEN} ���ложен�е �а�отает!${NC}"
echo -e "${BLUE} API: http://localhost:8000${NC}"
echo -e "${BLUE} Web App: ${WEBAPP_URL}${NC}"
echo ""
echo -e "${YELLOW}  �л� о�тановк� нажм�те Ctrl+C${NC}"
echo ""

# Ждем заве�шен��
wait

