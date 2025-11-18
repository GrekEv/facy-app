#!/bin/bash

# �к��пт дл� запу�ка п��ложен�� � ngrok туннелем
# И�пол�зован�е: ./start_with_ngrok.sh

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE} Запу�к Telegram Mini App � ngrok${NC}"
echo ""

# ��ове�ка нал�ч�� ngrok
if ! command -v ngrok &> /dev/null; then
    echo -e "${RED} ngrok не у�тановлен!${NC}"
    echo ""
    echo "У�танов�те ngrok:"
    echo "  macOS: brew install ngrok"
    echo "  Linux: wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
    echo "  Windows: https://ngrok.com/download"
    echo ""
    echo "За�е���т���уйте�� на https://ngrok.com � получ�те токен"
    echo "Затем в�полн�те: ngrok config add-authtoken ваш_токен"
    exit 1
fi

# ��ове�ка нал�ч�� Python
if ! command -v python &> /dev/null; then
    echo -e "${RED} Python не у�тановлен!${NC}"
    exit 1
fi

# ��ове�ка пе�еменн�� ок�ужен��
if [ -z "$BOT_TOKEN" ]; then
    echo -e "${YELLOW}  BOT_TOKEN не у�тановлен${NC}"
    echo "У�танов�те пе�еменну� ок�ужен��:"
    echo "  export BOT_TOKEN=ваш_токен_�ота"
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
    if [ ! -z "$NGROK_PID" ]; then
        kill $NGROK_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Запу�к API в фоне
echo -e "${BLUE} Запу�к API �е�ве�а...${NC}"
python run_api.py > api.log 2>&1 &
API_PID=$!

# Ждем запу�ка API
echo -e "${BLUE} Ож�дан�е запу�ка API (5 �екунд)...${NC}"
sleep 5

# ��ове�ка, что API запу�ен
if ! kill -0 $API_PID 2>/dev/null; then
    echo -e "${RED} API не запу�т�л��! ��ове��те api.log${NC}"
    exit 1
fi

# Запу�к ngrok
echo -e "${BLUE} Запу�к ngrok туннел�...${NC}"
ngrok http 8000 --log=stdout > ngrok.log 2>&1 &
NGROK_PID=$!

# Ждем запу�ка ngrok
echo -e "${BLUE} Ож�дан�е запу�ка ngrok (5 �екунд)...${NC}"
sleep 5

# �олучен�е URL �з ngrok API
echo -e "${BLUE} �олучен�е ngrok URL...${NC}"
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
    echo -e "${RED} �е удало�� получ�т� ngrok URL!${NC}"
    echo "��ове��те ngrok.log"
    cleanup
    exit 1
fi

echo ""
echo -e "${GREEN} API запу�ен на http://localhost:8000${NC}"
echo -e "${GREEN} ngrok туннел�: ${NGROK_URL}${NC}"
echo ""
echo -e "${YELLOW} ��Ж�О: О�нов�те WEBAPP_URL в BotFather:${NC}"
echo -e "${BLUE}   1. Отк�ойте @BotFather в Telegram${NC}"
echo -e "${BLUE}   2. /mybots � в��е��те �ота${NC}"
echo -e "${BLUE}   3. Bot Settings � Menu Button${NC}"
echo -e "${BLUE}   4. URL: ${NGROK_URL}${NC}"
echo ""
echo -e "${YELLOW} Также о�нов�те WEBAPP_URL в пе�еменн�� ок�ужен��:${NC}"
echo -e "${BLUE}   export WEBAPP_URL=${NGROK_URL}${NC}"
echo ""

# У�тановка WEBAPP_URL дл� �ота
export WEBAPP_URL=$NGROK_URL

# Запу�к �ота
echo -e "${BLUE}�� Запу�к Telegram �ота...${NC}"
echo -e "${YELLOW}  �л� о�тановк� нажм�те Ctrl+C${NC}"
echo ""

python main.py

# Оч��тка п�� в��оде
cleanup

