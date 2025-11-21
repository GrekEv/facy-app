#!/bin/bash
# Скрипт проверки подключения к Yandex Cloud и домена

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  ПРОВЕРКА YANDEX CLOUD + БД + ДОМЕН${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env файл не найден!${NC}"
    echo -e "${YELLOW}  Создайте .env файл или запустите switch_to_yandex_cloud.sh${NC}"
    exit 1
fi

echo -e "${BLUE}1. Проверка конфигурации .env...${NC}"

# Проверка DATABASE_URL
if grep -q "^DATABASE_URL=" .env; then
    DB_URL=$(grep "^DATABASE_URL=" .env | cut -d '=' -f2-)
    if [[ "$DB_URL" == *"yandexcloud.net"* ]]; then
        echo -e "${GREEN}✓ DATABASE_URL настроен для Yandex Cloud${NC}"
        # Показываем только хост (без пароля)
        DB_HOST=$(echo "$DB_URL" | sed -E 's|.*@([^:/]+).*|\1|')
        echo -e "  ${BLUE}Хост БД: ${DB_HOST}${NC}"
    else
        echo -e "${YELLOW}⚠ DATABASE_URL найден, но не для Yandex Cloud${NC}"
        echo -e "  ${BLUE}Текущий URL: ${DB_URL:0:50}...${NC}"
    fi
else
    echo -e "${RED}✗ DATABASE_URL не найден в .env${NC}"
fi

# Проверка WEBAPP_URL
if grep -q "^WEBAPP_URL=" .env; then
    WEBAPP_URL=$(grep "^WEBAPP_URL=" .env | cut -d '=' -f2-)
    echo -e "${GREEN}✓ WEBAPP_URL настроен: ${WEBAPP_URL}${NC}"
    
    # Извлекаем домен
    DOMAIN=$(echo "$WEBAPP_URL" | sed -E 's|https?://([^/]+).*|\1|' | sed 's|www\.||')
    echo -e "  ${BLUE}Домен: ${DOMAIN}${NC}"
else
    echo -e "${YELLOW}⚠ WEBAPP_URL не найден в .env${NC}"
    DOMAIN="onlyface.art"
    echo -e "  ${BLUE}Используется домен по умолчанию: ${DOMAIN}${NC}"
fi

echo ""
echo -e "${BLUE}2. Проверка подключения к базе данных...${NC}"

# Проверка подключения к БД через Python
if command -v python3 &> /dev/null; then
    if python3 check_connection.py 2>/dev/null; then
        echo -e "${GREEN}✓ Подключение к БД успешно${NC}"
    else
        echo -e "${RED}✗ Ошибка подключения к БД${NC}"
        echo -e "${YELLOW}  Запустите: python3 check_connection.py${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Python3 не найден, пропускаем проверку БД${NC}"
fi

echo ""
echo -e "${BLUE}3. Проверка DNS домена (${DOMAIN})...${NC}"

# Проверка DNS
if command -v dig &> /dev/null; then
    DOMAIN_IP=$(dig +short ${DOMAIN} 2>/dev/null | tail -1)
    if [ ! -z "$DOMAIN_IP" ]; then
        echo -e "${GREEN}✓ DNS резолвится: ${DOMAIN} -> ${DOMAIN_IP}${NC}"
    else
        echo -e "${RED}✗ DNS не резолвится для ${DOMAIN}${NC}"
    fi
else
    echo -e "${YELLOW}⚠ dig не найден, пропускаем проверку DNS${NC}"
fi

# Проверка доступности домена
echo ""
echo -e "${BLUE}4. Проверка доступности домена...${NC}"

if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 "https://${DOMAIN}/" 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
        echo -e "${GREEN}✓ Домен доступен (HTTP ${HTTP_CODE})${NC}"
    elif [ "$HTTP_CODE" = "000" ]; then
        echo -e "${RED}✗ Домен недоступен (таймаут)${NC}"
    else
        echo -e "${YELLOW}⚠ Домен отвечает с кодом ${HTTP_CODE}${NC}"
    fi
else
    echo -e "${YELLOW}⚠ curl не найден, пропускаем проверку доступности${NC}"
fi

# Проверка Nginx (если на сервере)
echo ""
if [ -d "/etc/nginx" ]; then
    echo -e "${BLUE}5. Проверка Nginx...${NC}"
    
    if sudo systemctl is-active --quiet nginx 2>/dev/null; then
        echo -e "${GREEN}✓ Nginx работает${NC}"
        
        # Проверка конфигурации для домена
        if sudo grep -q "${DOMAIN}" /etc/nginx/sites-enabled/* 2>/dev/null; then
            echo -e "${GREEN}✓ Nginx настроен для домена ${DOMAIN}${NC}"
        else
            echo -e "${YELLOW}⚠ Nginx не настроен для домена ${DOMAIN}${NC}"
        fi
    else
        echo -e "${RED}✗ Nginx не запущен${NC}"
    fi
else
    echo -e "${BLUE}5. Nginx не установлен (пропуск)${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  ИТОГОВАЯ СВОДКА${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Итоговая проверка
ALL_OK=true

if ! grep -q "yandexcloud.net" .env 2>/dev/null; then
    echo -e "${RED}✗ DATABASE_URL не настроен для Yandex Cloud${NC}"
    ALL_OK=false
fi

if [ -z "$WEBAPP_URL" ] || [ "$WEBAPP_URL" = "" ]; then
    echo -e "${RED}✗ WEBAPP_URL не настроен${NC}"
    ALL_OK=false
fi

if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}✓ Все основные настройки в порядке!${NC}"
    echo ""
    echo -e "${BLUE}Следующие шаги:${NC}"
    echo "  1. Убедитесь, что приложение запущено"
    echo "  2. Проверьте, что домен указывает на ваш сервер"
    echo "  3. Настройте SSL сертификат (Let's Encrypt)"
    echo ""
    echo -e "${BLUE}Полезные команды:${NC}"
    echo "  - Проверка БД: python3 check_connection.py"
    echo "  - Проверка сайта: curl -I https://${DOMAIN}"
    echo "  - Логи Nginx: sudo tail -f /var/log/nginx/error.log"
else
    echo -e "${YELLOW}⚠ Требуется настройка${NC}"
    echo ""
    echo -e "${BLUE}Рекомендации:${NC}"
    echo "  1. Запустите: ./switch_to_yandex_cloud.sh"
    echo "  2. Проверьте настройки в .env файле"
    echo "  3. Убедитесь, что домен указывает на IP сервера"
fi

echo ""


