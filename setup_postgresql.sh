#!/bin/bash
# Скрипт для настройки PostgreSQL в Яндекс.Облаке

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🐘 Настройка PostgreSQL в Яндекс.Облаке${NC}"
echo "=========================================="
echo ""

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

echo -e "${YELLOW}⚠️  ВАЖНО: Сначала создайте кластер PostgreSQL в консоли Яндекс.Облака!${NC}"
echo ""
echo -e "${BLUE}Инструкция:${NC}"
echo "1. Откройте https://cloud.yandex.ru"
echo "2. Managed Databases → PostgreSQL → Создать кластер"
echo "3. Настройте кластер (см. POSTGRESQL_SETUP.md)"
echo "4. Скопируйте данные для подключения"
echo ""
read -p "Нажмите Enter когда кластер создан, или Ctrl+C для отмены..."

echo ""
echo -e "${BLUE}Введите данные для подключения:${NC}"
echo ""

read -p "Хост (FQDN): " PG_HOST
read -p "Порт (обычно 6432): " PG_PORT
PG_PORT=${PG_PORT:-6432}

read -p "Имя базы данных: " PG_DB
read -p "Имя пользователя: " PG_USER
read -s -p "Пароль: " PG_PASSWORD
echo ""

echo ""
echo -e "${BLUE}🔧 Обновление requirements.txt...${NC}"

# Проверяем, есть ли asyncpg
if ! grep -q "asyncpg" requirements.txt; then
    echo "asyncpg==0.29.0  # Для PostgreSQL (асинхронный драйвер)" >> requirements.txt
    echo -e "${GREEN}✅ asyncpg добавлен в requirements.txt${NC}"
else
    echo -e "${YELLOW}⚠️  asyncpg уже есть в requirements.txt${NC}"
fi

echo ""
echo -e "${BLUE}🔧 Обновление .env файла...${NC}"

# Формируем строку подключения
DATABASE_URL="postgresql+asyncpg://${PG_USER}:${PG_PASSWORD}@${PG_HOST}:${PG_PORT}/${PG_DB}?ssl=require"

# Обновляем .env
if [ -f .env ]; then
    # Создаем резервную копию
    cp .env .env.backup.sqlite
    
    # Обновляем DATABASE_URL
    if grep -q "^DATABASE_URL=" .env; then
        sed -i "s|^DATABASE_URL=.*|DATABASE_URL=${DATABASE_URL}|g" .env
    else
        echo "DATABASE_URL=${DATABASE_URL}" >> .env
    fi
    
    echo -e "${GREEN}✅ DATABASE_URL обновлен в .env${NC}"
    echo -e "${YELLOW}⚠️  Резервная копия сохранена в .env.backup.sqlite${NC}"
else
    echo "DATABASE_URL=${DATABASE_URL}" > .env
    echo -e "${GREEN}✅ Создан новый .env файл${NC}"
fi

echo ""
echo -e "${BLUE}🔨 Пересборка Docker образа...${NC}"
docker compose -f docker-compose.prod.yml build --no-cache

echo ""
echo -e "${BLUE}🔄 Перезапуск приложения...${NC}"
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

echo ""
echo -e "${BLUE}⏳ Ожидание запуска (15 секунд)...${NC}"
sleep 15

echo ""
echo -e "${BLUE}📋 Проверка логов...${NC}"
docker compose -f docker-compose.prod.yml logs api --tail=30

echo ""
echo -e "${BLUE}📊 Статус контейнеров:${NC}"
docker compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}✅ Настройка завершена!${NC}"
echo ""
echo -e "${BLUE}📝 Следующие шаги:${NC}"
echo "1. Проверьте логи: docker compose -f docker-compose.prod.yml logs api"
echo "2. Проверьте health: curl http://localhost:8000/health"
echo "3. Если были данные в SQLite, выполните миграцию (см. POSTGRESQL_SETUP.md)"
echo ""
echo -e "${YELLOW}⚠️  Старая база SQLite сохранена в data/app.db.backup${NC}"

