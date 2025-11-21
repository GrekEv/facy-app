#!/bin/bash
# �к��пт дл� на�т�ойк� PostgreSQL в �ндек�.О�лаке

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}� �а�т�ойка PostgreSQL в �ндек�.О�лаке${NC}"
echo "=========================================="
echo ""

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

echo -e "${YELLOW}  ��Ж�О: �начала �оздайте кла�те� PostgreSQL в кон�ол� �ндек�.О�лака!${NC}"
echo ""
echo -e "${BLUE}Ин�т�укц��:${NC}"
echo "1. Отк�ойте https://cloud.yandex.ru"
echo "2. Managed Databases � PostgreSQL � �оздат� кла�те�"
echo "3. �а�т�ойте кла�те� (�м. POSTGRESQL_SETUP.md)"
echo "4. �коп��уйте данн�е дл� подкл�чен��"
echo ""
read -p "�ажм�те Enter ко�да кла�те� �оздан, �л� Ctrl+C дл� отмен�..."

echo ""
echo -e "${BLUE}�вед�те данн�е дл� подкл�чен��:${NC}"
echo ""

read -p "�о�т (FQDN): " PG_HOST
read -p "�о�т (о��чно 6432): " PG_PORT
PG_PORT=${PG_PORT:-6432}

read -p "Им� �аз� данн��: " PG_DB
read -p "Им� пол�зовател�: " PG_USER
read -s -p "�а�ол�: " PG_PASSWORD
echo ""

echo ""
echo -e "${BLUE} О�новлен�е requirements.txt...${NC}"

# ��ове��ем, е�т� л� asyncpg
if ! grep -q "asyncpg" requirements.txt; then
    echo "asyncpg==0.29.0  # �л� PostgreSQL (а��н��онн�й д�айве�)" >> requirements.txt
    echo -e "${GREEN} asyncpg до�авлен в requirements.txt${NC}"
else
    echo -e "${YELLOW}  asyncpg уже е�т� в requirements.txt${NC}"
fi

echo ""
echo -e "${BLUE} О�новлен�е .env файла...${NC}"

# Фо�м��уем �т�оку подкл�чен��
DATABASE_URL="postgresql+asyncpg://${PG_USER}:${PG_PASSWORD}@${PG_HOST}:${PG_PORT}/${PG_DB}?ssl=require"

# О�новл�ем .env
if [ -f .env ]; then
    # �оздаем �езе�вну� коп��
    cp .env .env.backup.sqlite
    
    # О�новл�ем DATABASE_URL
    if grep -q "^DATABASE_URL=" .env; then
        sed -i "s|^DATABASE_URL=.*|DATABASE_URL=${DATABASE_URL}|g" .env
    else
        echo "DATABASE_URL=${DATABASE_URL}" >> .env
    fi
    
    echo -e "${GREEN} DATABASE_URL о�новлен в .env${NC}"
    echo -e "${YELLOW}  �езе�вна� коп�� �о��анена в .env.backup.sqlite${NC}"
else
    echo "DATABASE_URL=${DATABASE_URL}" > .env
    echo -e "${GREEN} �оздан нов�й .env файл${NC}"
fi

echo ""
echo -e "${BLUE} �е�е��о�ка Docker о��аза...${NC}"
docker compose -f docker-compose.prod.yml build --no-cache

echo ""
echo -e "${BLUE}� �е�езапу�к п��ложен��...${NC}"
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

echo ""
echo -e "${BLUE} Ож�дан�е запу�ка (15 �екунд)...${NC}"
sleep 15

echo ""
echo -e "${BLUE} ��ове�ка ло�ов...${NC}"
docker compose -f docker-compose.prod.yml logs api --tail=30

echo ""
echo -e "${BLUE} �тату� контейне�ов:${NC}"
docker compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN} �а�т�ойка заве�шена!${NC}"
echo ""
echo -e "${BLUE} �леду���е ша��:${NC}"
echo "1. ��ове��те ло��: docker compose -f docker-compose.prod.yml logs api"
echo "2. ��ове��те health: curl http://localhost:8000/health"
echo "3. Е�л� ��л� данн�е в SQLite, в�полн�те м���ац�� (�м. POSTGRESQL_SETUP.md)"
echo ""
echo -e "${YELLOW}  �та�а� �аза SQLite �о��анена в data/app.db.backup${NC}"



