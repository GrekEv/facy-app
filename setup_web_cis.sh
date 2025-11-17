#!/bin/bash
# Скрипт настройки веб-приложения для РФ/РБ

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

echo -e "${BLUE}🌐 Настройка веб-приложения для РФ/РБ${NC}"
echo "======================================"
echo ""

# Запрос домена
echo -e "${BLUE}Введите ваш домен (по умолчанию: onlyface.art):${NC}"
read -r DOMAIN

if [ -z "$DOMAIN" ]; then
    DOMAIN="onlyface.art"
    echo -e "${GREEN}Используется домен по умолчанию: $DOMAIN${NC}"
fi

echo ""
echo -e "${BLUE}📦 Установка Nginx...${NC}"
sudo apt update
sudo apt install -y nginx

echo ""
echo -e "${BLUE}🔧 Создание конфигурации Nginx...${NC}"

# Создаем конфигурацию
sudo tee /etc/nginx/sites-available/facy > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 100M;

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

    location /static/ {
        alias $(pwd)/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /uploads/ {
        alias $(pwd)/uploads/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    location /generated/ {
        alias $(pwd)/generated/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
EOF

# Активация
sudo ln -sf /etc/nginx/sites-available/facy /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo ""
echo -e "${BLUE}🔍 Проверка конфигурации...${NC}"
sudo nginx -t

echo ""
echo -e "${BLUE}🔄 Перезапуск Nginx...${NC}"
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo -e "${GREEN}✅ Nginx настроен!${NC}"

echo ""
echo -e "${YELLOW}⚠️  Убедитесь, что DNS запись для $DOMAIN указывает на 158.160.96.182${NC}"
echo -e "${YELLOW}Нажмите Enter когда DNS настроен, или Ctrl+C для отмены...${NC}"
read -r

echo ""
echo -e "${BLUE}🔐 Установка SSL сертификата (Let's Encrypt)...${NC}"
sudo apt install -y certbot python3-certbot-nginx

echo ""
echo -e "${BLUE}Получение SSL сертификата...${NC}"
sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN" || {
    echo -e "${RED}❌ Не удалось получить сертификат!${NC}"
    echo -e "${YELLOW}Проверьте DNS настройки и попробуйте позже:${NC}"
    echo "sudo certbot --nginx -d $DOMAIN"
    exit 1
}

# Обновление .env
if [ -f .env ]; then
    echo ""
    echo -e "${BLUE}Обновление WEBAPP_URL в .env...${NC}"
    sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=https://$DOMAIN|g" .env
    echo -e "${GREEN}✅ WEBAPP_URL обновлен на https://$DOMAIN${NC}"
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
echo "  - HTTPS: https://$DOMAIN"
echo "  - HTTP: http://$DOMAIN"
echo "  - API Health: https://$DOMAIN/health"
echo ""
echo -e "${BLUE}📝 Следующие шаги:${NC}"
echo "1. Настройте Menu Button в BotFather:"
echo "   - Откройте @BotFather"
echo "   - /mybots → выберите бота"
echo "   - Bot Settings → Menu Button"
echo "   - URL: https://$DOMAIN"
echo ""
echo "2. Перезапустите приложение:"
echo "   docker compose -f docker-compose.prod.yml restart"
echo ""
echo "3. Проверьте работу:"
echo "   curl https://$DOMAIN/health"

