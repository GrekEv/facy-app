#!/bin/bash
# Скрипт для исправления ошибки 403 на статических файлах

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}Исправление ошибки 403 на статических файлах${NC}"
echo "=========================================="
echo ""

# Проверка, что скрипт запущен на сервере
if [ ! -d "/home/ubuntu" ]; then
    echo -e "${RED}Этот скрипт должен быть запущен на сервере!${NC}"
    echo "Подключитесь к серверу: ssh ubuntu@158.160.96.182"
    exit 1
fi

cd ~/facy-app || {
    echo -e "${RED}Директория ~/facy-app не найдена!${NC}"
    exit 1
}

# Получаем абсолютный путь к директории проекта
APP_DIR=$(pwd)
echo -e "${BLUE}Директория проекта: ${APP_DIR}${NC}"

# Проверяем существование статических файлов
if [ ! -f "${APP_DIR}/static/css/style.css" ]; then
    echo -e "${YELLOW}Предупреждение: ${APP_DIR}/static/css/style.css не найден${NC}"
fi

echo -e "${BLUE}1. Исправление прав доступа к статическим файлам...${NC}"

# Создаем директории если их нет
mkdir -p static/css static/js static/images uploads generated

# Устанавливаем правильные права
chmod -R 755 static/
chmod -R 755 uploads/
chmod -R 755 generated/

# Убеждаемся, что файлы читаемые (исправленная команда find)
find static/ -type f -exec chmod 644 {} +
find uploads/ -type f -exec chmod 644 {} +
find generated/ -type f -exec chmod 644 {} +

# Устанавливаем владельца (если нужно)
if [ -n "$USER" ]; then
    chown -R $USER:$USER static/ uploads/ generated/ 2>/dev/null || true
fi

echo -e "${GREEN}✓ Права доступа исправлены${NC}"

echo ""
echo -e "${BLUE}2. Удаление дублирующих конфигураций Nginx...${NC}"

# Удаляем все конфигурации из sites-enabled
sudo rm -f /etc/nginx/sites-enabled/*
echo -e "${GREEN}✓ Дублирующие конфигурации удалены${NC}"

echo ""
echo -e "${BLUE}3. Создание конфигурации Nginx с абсолютным путем...${NC}"

# Обновляем конфигурацию Nginx с абсолютным путем
sudo tee /etc/nginx/sites-available/onlyface > /dev/null <<EOF
server {
    listen 80;
    server_name onlyface.art www.onlyface.art;

    client_max_body_size 100M;

    # Статические файлы - отдаем напрямую через Nginx (абсолютный путь)
    location /static/ {
        alias ${APP_DIR}/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    location /uploads/ {
        alias ${APP_DIR}/uploads/;
        expires 7d;
        add_header Cache-Control "public";
        access_log off;
    }
    
    location /generated/ {
        alias ${APP_DIR}/generated/;
        expires 7d;
        add_header Cache-Control "public";
        access_log off;
    }

    # Все остальное проксируем на FastAPI
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
EOF

# Активируем конфигурацию (уже удалили все выше, так что это единственная)
sudo ln -sf /etc/nginx/sites-available/onlyface /etc/nginx/sites-enabled/

echo -e "${GREEN}✓ Конфигурация Nginx создана с абсолютным путем: ${APP_DIR}${NC}"

echo ""
echo -e "${BLUE}4. Проверка конфигурации Nginx...${NC}"
if sudo nginx -t; then
    echo -e "${GREEN}✓ Конфигурация Nginx корректна${NC}"
else
    echo -e "${RED}✗ Ошибка в конфигурации Nginx!${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}5. Перезапуск Nginx...${NC}"
sudo systemctl restart nginx

echo ""
echo -e "${GREEN}✓ Готово! Ошибка 403 должна быть исправлена${NC}"
echo ""
echo -e "${BLUE}Проверка:${NC}"
echo "  curl -I http://localhost/static/css/style.css"
echo "  curl -I http://localhost/static/js/app.js"
echo ""
echo -e "${BLUE}Используемый путь: ${APP_DIR}${NC}"
echo ""
echo -e "${BLUE}Если проблема сохраняется, проверьте:${NC}"
echo "  1. Логи Nginx: sudo tail -f /var/log/nginx/error.log"
echo "  2. Права доступа: ls -la ${APP_DIR}/static/"
echo "  3. Существование файлов: ls -la ${APP_DIR}/static/css/style.css"
echo "  4. Конфигурация: sudo cat /etc/nginx/sites-available/onlyface | grep -A 3 'location /static'"

