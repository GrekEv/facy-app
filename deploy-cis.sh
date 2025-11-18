#!/bin/bash

# �к��пт дл� депло� Facy на �е�в��� ���
# �одде�ж�вает: Yandex Cloud, Timeweb, Selectel, Beget

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE} �еплой Facy на �е�в��� ���${NC}"
echo "================================"
echo ""

# ��ове�ка что м� на �е�ве�е
if [ ! -f /.dockerenv ] && [ ! -d /app ]; then
    echo -e "${YELLOW}�тот �к��пт должен запу�кат��� на �е�ве�е${NC}"
    echo "�одкл�ч�те�� к �е�ве�у по SSH � запу�т�те �к��пт там"
    exit 1
fi

# О�новлен�е ���тем�
echo -e "${BLUE}О�новлен�е ���тем�...${NC}"
sudo apt update && sudo apt upgrade -y

# У�тановка Docker
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}У�тановка Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN} Docker у�тановлен${NC}"
else
    echo -e "${GREEN} Docker уже у�тановлен${NC}"
fi

# У�тановка Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}У�тановка Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN} Docker Compose у�тановлен${NC}"
else
    echo -e "${GREEN} Docker Compose уже у�тановлен${NC}"
fi

# У�тановка Git
if ! command -v git &> /dev/null; then
    echo -e "${BLUE}У�тановка Git...${NC}"
    sudo apt install git -y
    echo -e "${GREEN} Git у�тановлен${NC}"
fi

# �лон��ован�е �епоз�то��� (е�л� е�е не клон��ован)
if [ ! -d "facy-app" ]; then
    echo -e "${BLUE}�лон��ован�е �епоз�то���...${NC}"
    git clone https://github.com/GrekEv/facy-app.git
    cd facy-app
else
    echo -e "${BLUE}О�новлен�е �епоз�то���...${NC}"
    cd facy-app
    git pull
fi

# �оздан�е .env файла (е�л� не �у�е�твует)
if [ ! -f .env ]; then
    echo -e "${BLUE}�оздан�е .env файла...${NC}"
    cat > .env << EOF
BOT_TOKEN=8374729179:AAG7wyo467ksUQgNyoESNzc09Wn0UBS7T7g
WEBAPP_URL=https://ваш-домен.ru
ENVIRONMENT=production
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
HOST=0.0.0.0
PORT=8000
EOF
    echo -e "${YELLOW}  От�едакт��уйте .env файл пе�ед запу�ком!${NC}"
    echo "�ажм�те Enter дл� п�одолжен�� �л� Ctrl+C дл� в��ода..."
    read
else
    echo -e "${GREEN} .env файл �у�е�твует${NC}"
fi

# �оздан�е д��екто��й
echo -e "${BLUE}�оздан�е д��екто��й...${NC}"
mkdir -p data uploads generated temp
echo -e "${GREEN} ���екто��� �оздан�${NC}"

# Запу�к че�ез Docker Compose
echo -e "${BLUE}Запу�к п��ложен��...${NC}"
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo -e "${GREEN} �еплой заве�шен!${NC}"
echo ""
echo "��ове�ка �тату�а:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "��о�мот� ло�ов:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "О�тановка:"
echo "  docker-compose -f docker-compose.prod.yml down"
echo ""

