#!/bin/bash
# Скрипт автоматической настройки домена с reg.ru

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🌐 Настройка домена для приложения${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Проверка, что скрипт запущен на сервере
if [ ! -d "/home/ubuntu" ]; then
    echo -e "${RED}❌ Этот скрипт должен быть запущен на сервере!${NC}"
    echo "Подключитесь к серверу: ssh ubuntu@158.160.96.182"
    exit 1
fi

# Запрос домена
echo -e "${BLUE}Введите ваш домен (например: example.ru):${NC}"
read -r DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ Домен не указан!${NC}"
    exit 1
fi

# Убираем протокол и слеши из домена
DOMAIN=$(echo "$DOMAIN" | sed 's|^https\?://||' | sed 's|/$||' | sed 's|^www\.||')
# Если домен начинается с www, оставляем только без www (www будет добавлен отдельно)
DOMAIN_BASE="$DOMAIN"

# Запрос email для SSL
echo -e "${BLUE}Введите ваш email для SSL сертификата:${NC}"
read -r EMAIL

if [ -z "$EMAIL" ]; then
    echo -e "${YELLOW}⚠️  Email не указан, будет использован admin@$DOMAIN_BASE${NC}"
    EMAIL="admin@$DOMAIN_BASE"
fi

echo ""
echo -e "${BLUE}📋 Настройки:${NC}"
echo -e "  Домен: ${GREEN}$DOMAIN_BASE${NC}"
echo -e "  Email: ${GREEN}$EMAIL${NC}"
echo -e "  IP сервера: ${GREEN}158.160.96.182${NC}"
echo ""

echo -e "${YELLOW}⚠️  ВАЖНО: Перед продолжением настройте DNS записи на reg.ru!${NC}"
echo -e "${YELLOW}   Добавьте A-запись для $DOMAIN_BASE → 158.160.96.182${NC}"
echo -e "${YELLOW}   Добавьте A-запись для www.$DOMAIN_BASE → 158.160.96.182${NC}"
echo ""
read -p "Нажмите Enter когда DNS настроен, или Ctrl+C для отмены..."

echo ""
echo -e "${BLUE}📦 Установка Nginx...${NC}"
sudo apt update
sudo apt install -y nginx

echo ""
echo -e "${BLUE}🔧 Создание конфигурации Nginx...${NC}"
cd ~/facy-app || {
    echo -e "${RED}❌ Директория ~/facy-app не найдена!${NC}"
    exit 1
}

sudo tee /etc/nginx/sites-available/facy > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_BASE www.$DOMAIN_BASE;

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
echo -e "${BLUE}🔍 Проверка DNS...${NC}"
echo -e "${YELLOW}Проверяю, что домен указывает на сервер...${NC}"

# Проверка DNS
DNS_IP=$(dig +short $DOMAIN_BASE | tail -1)
if [ "$DNS_IP" = "158.160.96.182" ]; then
    echo -e "${GREEN}✅ DNS настроен правильно!${NC}"
else
    echo -e "${YELLOW}⚠️  DNS еще не настроен или не распространился${NC}"
    echo -e "${YELLOW}   Текущий IP: $DNS_IP${NC}"
    echo -e "${YELLOW}   Ожидаемый IP: 158.160.96.182${NC}"
    echo ""
    read -p "Продолжить установку SSL? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Установка SSL отменена. Настройте DNS и запустите скрипт снова.${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}🔐 Установка SSL сертификата (Let's Encrypt)...${NC}"
sudo apt install -y certbot python3-certbot-nginx

echo ""
echo -e "${BLUE}Получение SSL сертификата...${NC}"
sudo certbot --nginx -d "$DOMAIN_BASE" -d "www.$DOMAIN_BASE" \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --redirect || {
    echo -e "${YELLOW}⚠️  Автоматическая установка SSL не удалась${NC}"
    echo -e "${YELLOW}Попробуйте установить вручную:${NC}"
    echo "sudo certbot --nginx -d $DOMAIN_BASE -d www.$DOMAIN_BASE"
    exit 1
}

echo ""
echo -e "${GREEN}✅ SSL сертификат установлен!${NC}"

# Обновление .env
echo ""
echo -e "${BLUE}📝 Обновление конфигурации приложения...${NC}"
if [ -f .env ]; then
    if grep -q "WEBAPP_URL=" .env; then
        sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=https://$DOMAIN_BASE|g" .env
        echo -e "${GREEN}✅ WEBAPP_URL обновлен на https://$DOMAIN_BASE${NC}"
    else
        echo "WEBAPP_URL=https://$DOMAIN_BASE" >> .env
        echo -e "${GREEN}✅ WEBAPP_URL добавлен в .env${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Файл .env не найден${NC}"
fi

# Настройка firewall
echo ""
echo -e "${BLUE}🔥 Настройка firewall...${NC}"
sudo ufw allow 22/tcp 2>/dev/null || true
sudo ufw allow 80/tcp 2>/dev/null || true
sudo ufw allow 443/tcp 2>/dev/null || true
sudo ufw --force enable 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ Готово!${NC}"
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}🎉 Домен настроен!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${BLUE}📋 Информация:${NC}"
echo -e "  - HTTPS: ${GREEN}https://$DOMAIN_BASE${NC}"
echo -e "  - HTTP: ${GREEN}http://$DOMAIN_BASE${NC}"
echo -e "  - API Health: ${GREEN}https://$DOMAIN_BASE/health${NC}"
echo ""
echo -e "${BLUE}📝 Следующие шаги:${NC}"
echo -e "1. Настройте Menu Button в BotFather:"
echo -e "   - Откройте @BotFather"
echo -e "   - /mybots → выберите бота → Bot Settings → Menu Button"
echo -e "   - URL: ${GREEN}https://$DOMAIN_BASE${NC}"
echo ""
echo -e "2. Перезапустите приложение:"
echo -e "   ${GREEN}docker compose -f docker-compose.prod.yml restart${NC}"
echo ""
echo -e "3. Проверьте работу:"
echo -e "   ${GREEN}curl https://$DOMAIN_BASE/health${NC}"
echo ""
echo -e "${GREEN}✅ Ваше приложение доступно на https://$DOMAIN_BASE${NC}"

