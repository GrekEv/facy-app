#!/bin/bash
# �к��пт дл� �азве�т�ван�� на �е�ве�е Yandex Cloud

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE} �азве�т�ван�е на �е�ве�е Yandex Cloud${NC}"
echo "=========================================="
echo ""

# ��ове�ка, что �к��пт запу�ен на �е�ве�е
if [ ! -d "/home/ubuntu" ]; then
    echo -e "${RED} �тот �к��пт должен ��т� запу�ен на �е�ве�е!${NC}"
    echo "�одкл�ч�те�� к �е�ве�у: ssh ubuntu@158.160.96.182"
    exit 1
fi

cd ~/facy-app || {
    echo -e "${YELLOW} �оздан�е д��екто��� п�оекта...${NC}"
    mkdir -p ~/facy-app
    cd ~/facy-app
}

echo -e "${BLUE}� О�новлен�е ���тем�...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${BLUE} У�тановка зав���мо�тей...${NC}"
sudo apt install -y python3 python3-pip python3-venv git curl

# У�тановка Docker
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE} У�тановка Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    rm get-docker.sh
    echo -e "${GREEN} Docker у�тановлен${NC}"
else
    echo -e "${GREEN} Docker уже у�тановлен${NC}"
fi

# У�тановка Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE} У�тановка Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN} Docker Compose у�тановлен${NC}"
else
    echo -e "${GREEN} Docker Compose уже у�тановлен${NC}"
fi

# �оздан�е .env файла
echo -e "${BLUE}�  �оздан�е .env файла...${NC}"
cat > .env << 'ENVEOF'
BOT_TOKEN=8374729179:AAG7wyo467ksUQgNyoESNzc09Wn0UBS7T7g
WEBAPP_URL=https://onlyface.art
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql+asyncpg://facy_user:etxX4gk272PdJYH@rc1a-6t9pb3se81b4idf5.mdb.yandexcloud.net:6432/facy_db?ssl=require
ENVEOF

echo -e "${GREEN} .env файл �оздан${NC}"

# У�тановка Python зав���мо�тей
echo -e "${BLUE}� У�тановка Python зав���мо�тей...${NC}"
pip3 install -r requirements.txt

echo -e "${BLUE} Запу�к че�ез Docker Compose...${NC}"
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

echo ""
echo -e "${GREEN} ���ложен�е �азве�нуто!${NC}"
echo ""
echo -e "${BLUE} ��ове�ка �тату�а:${NC}"
docker compose -f docker-compose.prod.yml ps

echo ""
echo -e "${BLUE} �олезн�е команд�:${NC}"
echo "  - Ло��: docker compose -f docker-compose.prod.yml logs -f"
echo "  - �тату�: docker compose -f docker-compose.prod.yml ps"
echo "  - �е�езапу�к: docker compose -f docker-compose.prod.yml restart"
echo "  - О�тановка: docker compose -f docker-compose.prod.yml down"

echo ""
echo -e "${YELLOW}  Е�л� Docker не �а�отает, пе�езайд�те в ���тему:${NC}"
echo "  exit"
echo "  ssh ubuntu@158.160.96.182"


