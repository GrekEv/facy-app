#!/bin/bash

# Скрипт для деплоя Facy на сервисы СНГ
# Поддерживает: Yandex Cloud, Timeweb, Selectel, Beget

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Деплой Facy на сервисы СНГ${NC}"
echo "================================"
echo ""

# Проверка что мы на сервере
if [ ! -f /.dockerenv ] && [ ! -d /app ]; then
    echo -e "${YELLOW}Этот скрипт должен запускаться на сервере${NC}"
    echo "Подключитесь к серверу по SSH и запустите скрипт там"
    exit 1
fi

# Обновление системы
echo -e "${BLUE}Обновление системы...${NC}"
sudo apt update && sudo apt upgrade -y

# Установка Docker
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}Установка Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✓ Docker установлен${NC}"
else
    echo -e "${GREEN}✓ Docker уже установлен${NC}"
fi

# Установка Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}Установка Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose установлен${NC}"
else
    echo -e "${GREEN}✓ Docker Compose уже установлен${NC}"
fi

# Установка Git
if ! command -v git &> /dev/null; then
    echo -e "${BLUE}Установка Git...${NC}"
    sudo apt install git -y
    echo -e "${GREEN}✓ Git установлен${NC}"
fi

# Клонирование репозитория (если еще не клонирован)
if [ ! -d "facy-app" ]; then
    echo -e "${BLUE}Клонирование репозитория...${NC}"
    git clone https://github.com/GrekEv/facy-app.git
    cd facy-app
else
    echo -e "${BLUE}Обновление репозитория...${NC}"
    cd facy-app
    git pull
fi

# Создание .env файла (если не существует)
if [ ! -f .env ]; then
    echo -e "${BLUE}Создание .env файла...${NC}"
    cat > .env << EOF
BOT_TOKEN=8374729179:AAG7wyo467ksUQgNyoESNzc09Wn0UBS7T7g
WEBAPP_URL=https://ваш-домен.ru
ENVIRONMENT=production
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
HOST=0.0.0.0
PORT=8000
EOF
    echo -e "${YELLOW}⚠️  Отредактируйте .env файл перед запуском!${NC}"
    echo "Нажмите Enter для продолжения или Ctrl+C для выхода..."
    read
else
    echo -e "${GREEN}✓ .env файл существует${NC}"
fi

# Создание директорий
echo -e "${BLUE}Создание директорий...${NC}"
mkdir -p data uploads generated temp
echo -e "${GREEN}✓ Директории созданы${NC}"

# Запуск через Docker Compose
echo -e "${BLUE}Запуск приложения...${NC}"
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo -e "${GREEN}✅ Деплой завершен!${NC}"
echo ""
echo "Проверка статуса:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "Просмотр логов:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "Остановка:"
echo "  docker-compose -f docker-compose.prod.yml down"
echo ""

