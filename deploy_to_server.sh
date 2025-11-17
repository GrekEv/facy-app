#!/bin/bash
# Скрипт для развертывания на сервере Yandex Cloud

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Развертывание на сервере Yandex Cloud${NC}"
echo "=========================================="
echo ""

# Проверка, что скрипт запущен на сервере
if [ ! -d "/home/ubuntu" ]; then
    echo -e "${RED}❌ Этот скрипт должен быть запущен на сервере!${NC}"
    echo "Подключитесь к серверу: ssh ubuntu@158.160.96.182"
    exit 1
fi

cd ~/facy-app || {
    echo -e "${YELLOW}📁 Создание директории проекта...${NC}"
    mkdir -p ~/facy-app
    cd ~/facy-app
}

echo -e "${BLUE}📦 Обновление системы...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${BLUE}📥 Установка зависимостей...${NC}"
sudo apt install -y python3 python3-pip python3-venv git curl

# Установка Docker
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}🐳 Установка Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker установлен${NC}"
else
    echo -e "${GREEN}✅ Docker уже установлен${NC}"
fi

# Установка Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}🐳 Установка Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose установлен${NC}"
else
    echo -e "${GREEN}✅ Docker Compose уже установлен${NC}"
fi

# Создание .env файла
echo -e "${BLUE}⚙️  Создание .env файла...${NC}"
cat > .env << 'ENVEOF'
BOT_TOKEN=8374729179:AAG7wyo467ksUQgNyoESNzc09Wn0UBS7T7g
WEBAPP_URL=https://onlyface.art
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql+asyncpg://facy_user:etxX4gk272PdJYH@rc1a-6t9pb3se81b4idf5.mdb.yandexcloud.net:6432/facy_db?ssl=require
ENVEOF

echo -e "${GREEN}✅ .env файл создан${NC}"

# Установка Python зависимостей
echo -e "${BLUE}📦 Установка Python зависимостей...${NC}"
pip3 install -r requirements.txt

echo -e "${BLUE}🐳 Запуск через Docker Compose...${NC}"
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

echo ""
echo -e "${GREEN}✅ Приложение развернуто!${NC}"
echo ""
echo -e "${BLUE}📋 Проверка статуса:${NC}"
docker compose -f docker-compose.prod.yml ps

echo ""
echo -e "${BLUE}📝 Полезные команды:${NC}"
echo "  - Логи: docker compose -f docker-compose.prod.yml logs -f"
echo "  - Статус: docker compose -f docker-compose.prod.yml ps"
echo "  - Перезапуск: docker compose -f docker-compose.prod.yml restart"
echo "  - Остановка: docker compose -f docker-compose.prod.yml down"

echo ""
echo -e "${YELLOW}⚠️  Если Docker не работает, перезайдите в систему:${NC}"
echo "  exit"
echo "  ssh ubuntu@158.160.96.182"


