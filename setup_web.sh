#!/bin/bash
# Скрипт для настройки веб-приложения с Nginx и HTTPS

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🌐 Настройка веб-приложения${NC}"
echo "================================"
echo ""

# Проверка, что мы на сервере
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}⚠️  Не запускайте скрипт от root. Используйте обычного пользователя.${NC}"
    exit 1
fi

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

# Запрос домена
echo -e "${BLUE}Введите ваш домен (или нажмите Enter для использования IP):${NC}"
read -r DOMAIN

if [ -z "$DOMAIN" ]; then
    DOMAIN="158.160.96.182"
    USE_IP=true
    echo -e "${YELLOW}Используется IP адрес: $DOMAIN${NC}"
else
    USE_IP=false
    echo -e "${GREEN}Используется домен: $DOMAIN${NC}"
fi

echo ""
echo -e "${BLUE}📦 Установка Nginx...${NC}"
sudo apt update
sudo apt install -y nginx

echo ""
echo -e "${BLUE}🔧 Создание конфигурации Nginx...${NC}"

# Создаем конфигурацию Nginx
sudo tee /etc/nginx/sites-available/facy > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    # Увеличение размера загружаемых файлов
    client_max_body_size 100M;

    # Основное приложение
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Для WebSocket (если используется)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Статические файлы
    location /static/ {
        alias $(pwd)/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Загруженные файлы
    location /uploads/ {
        alias $(pwd)/uploads/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Сгенерированные файлы
    location /generated/ {
        alias $(pwd)/generated/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
EOF

# Активируем конфигурацию
sudo ln -sf /etc/nginx/sites-available/facy /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Проверяем конфигурацию
echo ""
echo -e "${BLUE}🔍 Проверка конфигурации Nginx...${NC}"
sudo nginx -t

# Перезапускаем Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo -e "${GREEN}✅ Nginx настроен!${NC}"

# Настройка SSL (только если есть домен)
if [ "$USE_IP" = false ]; then
    echo ""
    echo -e "${BLUE}🔐 Настройка SSL сертификата...${NC}"
    echo -e "${YELLOW}Убедитесь, что DNS запись для $DOMAIN указывает на IP: 158.160.96.182${NC}"
    echo -e "${YELLOW}Нажмите Enter когда DNS будет настроен, или Ctrl+C для пропуска...${NC}"
    read -r
    
    echo ""
    echo -e "${BLUE}Установка Certbot...${NC}"
    sudo apt install -y certbot python3-certbot-nginx
    
    echo ""
    echo -e "${BLUE}Получение SSL сертификата...${NC}"
    sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@$DOMAIN || {
        echo -e "${YELLOW}⚠️  Не удалось получить сертификат. Проверьте DNS настройки.${NC}"
        echo -e "${YELLOW}Вы можете настроить SSL позже командой:${NC}"
        echo "sudo certbot --nginx -d $DOMAIN"
    }
    
    # Обновляем WEBAPP_URL в .env
    if [ -f .env ]; then
        echo ""
        echo -e "${BLUE}Обновление WEBAPP_URL в .env...${NC}"
        sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=https://$DOMAIN|g" .env
        echo -e "${GREEN}✅ WEBAPP_URL обновлен на https://$DOMAIN${NC}"
    fi
else
    echo ""
    echo -e "${YELLOW}⚠️  Для Telegram Mini App требуется HTTPS.${NC}"
    echo -e "${YELLOW}Рекомендуется настроить домен и SSL сертификат.${NC}"
    echo ""
    echo -e "${BLUE}Текущий URL: http://$DOMAIN${NC}"
    if [ -f .env ]; then
        sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=http://$DOMAIN|g" .env
    fi
fi

# Настройка firewall
echo ""
echo -e "${BLUE}🔥 Настройка firewall...${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable || true

echo ""
echo -e "${GREEN}✅ Веб-приложение настроено!${NC}"
echo ""
echo -e "${BLUE}📋 Информация:${NC}"
echo "  - HTTP: http://$DOMAIN"
if [ "$USE_IP" = false ]; then
    echo "  - HTTPS: https://$DOMAIN"
fi
echo "  - API Health: http://$DOMAIN/health"
echo ""
echo -e "${BLUE}📝 Следующие шаги:${NC}"
echo "1. Обновите WEBAPP_URL в BotFather:"
echo "   - Откройте @BotFather"
echo "   - /mybots → выберите бота"
echo "   - Bot Settings → Menu Button"
echo "   - URL: http://$DOMAIN (или https://$DOMAIN если настроен SSL)"
echo ""
echo "2. Перезапустите приложение:"
echo "   docker compose -f docker-compose.prod.yml restart"
echo ""
echo "3. Проверьте работу:"
echo "   curl http://$DOMAIN/health"


