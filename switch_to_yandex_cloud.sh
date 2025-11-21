#!/bin/bash
# Скрипт для переключения на Yandex Cloud

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Переключение на Yandex Cloud${NC}"
echo "=========================================="
echo ""

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}.env файл не найден. Создаю новый...${NC}"
    touch .env
fi

# Создаем резервную копию
if [ -f ".env" ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}Создана резервная копия .env${NC}"
fi

# Запрашиваем данные для Yandex Cloud
echo -e "${BLUE}Введите данные для подключения к Yandex Cloud:${NC}"
echo ""

read -p "DATABASE_URL (например: postgresql+asyncpg://user:password@rc1a-xxx.mdb.yandexcloud.net:6432/dbname?ssl=require): " DB_URL

if [ -z "$DB_URL" ]; then
    # Используем значение по умолчанию из deploy_to_server.sh
    DB_URL="postgresql+asyncpg://facy_user:etxX4gk272PdJYH@rc1a-6t9pb3se81b4idf5.mdb.yandexcloud.net:6432/facy_db?ssl=require"
    echo -e "${YELLOW}Используется значение по умолчанию${NC}"
fi

read -p "WEBAPP_URL (например: https://onlyface.art) [оставить текущее]: " WEBAPP_URL

# Читаем текущий BOT_TOKEN если есть
if [ -f ".env" ]; then
    CURRENT_BOT_TOKEN=$(grep "^BOT_TOKEN=" .env | cut -d '=' -f2- || echo "")
    CURRENT_WEBAPP_URL=$(grep "^WEBAPP_URL=" .env | cut -d '=' -f2- || echo "")
fi

# Обновляем или создаем .env файл
{
    if [ ! -z "$CURRENT_BOT_TOKEN" ]; then
        echo "BOT_TOKEN=$CURRENT_BOT_TOKEN"
    else
        read -p "BOT_TOKEN: " BOT_TOKEN
        echo "BOT_TOKEN=$BOT_TOKEN"
    fi
    
    if [ ! -z "$WEBAPP_URL" ]; then
        echo "WEBAPP_URL=$WEBAPP_URL"
    elif [ ! -z "$CURRENT_WEBAPP_URL" ]; then
        echo "WEBAPP_URL=$CURRENT_WEBAPP_URL"
    else
        echo "WEBAPP_URL=https://onlyface.art"
    fi
    
    echo "ENVIRONMENT=production"
    echo "HOST=0.0.0.0"
    echo "PORT=8000"
    echo "DATABASE_URL=$DB_URL"
} > .env

echo ""
echo -e "${GREEN}✓ .env файл обновлен для Yandex Cloud${NC}"
echo ""
echo -e "${BLUE}Проверка подключения...${NC}"
echo ""

# Проверяем подключение к базе данных
if command -v python3 &> /dev/null; then
    python3 check_connection.py || echo -e "${YELLOW}Не удалось проверить подключение автоматически${NC}"
else
    echo -e "${YELLOW}Python3 не найден. Проверьте подключение вручную${NC}"
fi

echo ""
echo -e "${GREEN}Готово! Конфигурация переключена на Yandex Cloud${NC}"
echo ""
echo -e "${BLUE}Полезные команды:${NC}"
echo "  - Проверка подключения: python3 check_connection.py"
echo "  - Запуск приложения: python3 main.py"
echo "  - Просмотр логов: docker compose logs -f (если используете Docker)"

