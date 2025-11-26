#!/bin/bash
# �к��пт дл� п�ове�к� подкл�чен�� к �е�ве�у Yandex Cloud

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}��ове�ка подкл�чен�� к �е�ве�у Yandex Cloud${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# IP ад�е� �е�ве�а (замен�те на ваш)
SERVER_IP="${1:-158.160.96.182}"
SERVER_USER="${2:-ubuntu}"

echo -e "${BLUE}�е�ве�: ${SERVER_USER}@${SERVER_IP}${NC}"
echo ""

# ��ове�ка 1: Ping
echo -e "${BLUE}1. ��ове�ка до�тупно�т� �е�ве�а (ping)...${NC}"
if ping -c 3 -W 2 "$SERVER_IP" > /dev/null 2>&1; then
    echo -e "${GREEN} �е�ве� до�тупен${NC}"
else
    echo -e "${RED} �е�ве� недо�тупен${NC}"
    exit 1
fi

echo ""

# ��ове�ка 2: SSH подкл�чен�е
echo -e "${BLUE}2. ��ове�ка SSH подкл�чен��...${NC}"
if ssh -o ConnectTimeout=5 -o BatchMode=yes "${SERVER_USER}@${SERVER_IP}" "echo 'SSH подкл�чен�е �а�отает'" 2>/dev/null; then
    echo -e "${GREEN} SSH подкл�чен�е �а�отает${NC}"
else
    echo -e "${YELLOW}  SSH подкл�чен�е т�е�ует аутент�ф�кац��${NC}"
    echo -e "${BLUE}   �оп�о�уйте подкл�ч�т��� в�учну�:${NC}"
    echo -e "${BLUE}   ssh ${SERVER_USER}@${SERVER_IP}${NC}"
fi

echo ""

# ��ове�ка 3: ��ове�ка п��ложен�� на �е�ве�е (е�л� SSH до�тупен)
echo -e "${BLUE}3. ��ове�ка п��ложен�� на �е�ве�е...${NC}"
if ssh -o ConnectTimeout=5 "${SERVER_USER}@${SERVER_IP}" "cd ~/facy-app 2>/dev/null && docker compose -f docker-compose.prod.yml ps 2>/dev/null" 2>/dev/null; then
    echo -e "${GREEN} ���ложен�е найдено на �е�ве�е${NC}"
    
    # ��ове�ка �тату�а контейне�ов
    echo -e "${BLUE}   �тату� контейне�ов:${NC}"
    ssh -o ConnectTimeout=5 "${SERVER_USER}@${SERVER_IP}" "cd ~/facy-app && docker compose -f docker-compose.prod.yml ps" 2>/dev/null || true
    
    # ��ове�ка подкл�чен�� к �азе данн�� на �е�ве�е
    echo ""
    echo -e "${BLUE}4. ��ове�ка подкл�чен�� к �азе данн�� на �е�ве�е...${NC}"
    ssh -o ConnectTimeout=5 "${SERVER_USER}@${SERVER_IP}" "cd ~/facy-app && python3 check_connection.py 2>/dev/null" 2>/dev/null || {
        echo -e "${YELLOW}  �к��пт п�ове�к� не найден на �е�ве�е${NC}"
        echo -e "${BLUE}   За��уз�те check_connection.py на �е�ве�${NC}"
    }
else
    echo -e "${YELLOW}  �е удало�� п�ове��т� п��ложен�е на �е�ве�е${NC}"
    echo -e "${BLUE}   �одкл�ч�те�� к �е�ве�у в�учну�:${NC}"
    echo -e "${BLUE}   ssh ${SERVER_USER}@${SERVER_IP}${NC}"
fi

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}��ове�ка заве�шена${NC}"
echo -e "${BLUE}============================================================${NC}"

