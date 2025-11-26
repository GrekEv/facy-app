#!/bin/bash
# Команды для создания скрипта на сервере

cat << 'EOF'
# Выполните эти команды на сервере:

ssh root@72.56.85.215 << 'SERVER_SCRIPT'
cd ~/facy-app

cat > setup_domain_onlyface.sh << 'SCRIPT_EOF'
#!/bin/bash
# Скрипт настройки домена onlyface.art на сервере Timeweb.cloud
# IP сервера: 72.56.85.215

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

DOMAIN="onlyface.art"
SERVER_IP="72.56.85.215"

echo -e "${BLUE}=========================================="
echo -e "Настройка домена $DOMAIN"
echo -e "IP сервера: $SERVER_IP"
echo -e "==========================================${NC}"
echo ""

cd ~/facy-app || cd /root/facy-app || {
    echo -e "${RED}Директория приложения не найдена!${NC}"
    exit 1
}

echo -e "${YELLOW}Настройте DNS записи в Timeweb перед продолжением${NC}"
echo "Домены и SSL → $DOMAIN → DNS-записи"
echo "Добавьте A-записи: @ → $SERVER_IP, www → $SERVER_IP"
echo -e "${YELLOW}Нажмите Enter когда DNS настроен...${NC}"
read -r

echo ""
echo -e "${BLUE}Шаг 1: Установка Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    sudo apt update
    sudo apt install -y nginx
    echo -e "${GREEN}✓ Nginx установлен${NC}"
else
    echo -e "${GREEN}✓ Nginx уже установлен${NC}"
fi

echo ""
echo -e "${BLUE}Шаг 2: Создание конфигурации Nginx...${NC}"

sudo tee /etc/nginx/sites-available/onlyface > /dev/null <<NGINX_EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \\\$host;
        proxy_set_header X-Real-IP \\\$remote_addr;
        proxy_set_header X-Forwarded-For \\\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\\$scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\\$http_upgrade;
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
NGINX_EOF

sudo ln -sf /etc/nginx/sites-available/onlyface /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo ""
echo -e "${BLUE}Шаг 3: Проверка конфигурации Nginx...${NC}"
sudo nginx -t

echo ""
echo -e "${BLUE}Шаг 4: Перезапуск Nginx...${NC}"
sudo systemctl restart nginx
sudo systemctl enable nginx

echo -e "${GREEN}✓ Nginx настроен и запущен!${NC}"

echo ""
echo -e "${BLUE}Шаг 5: Установка SSL сертификата (Let's Encrypt)...${NC}"
if ! command -v certbot &> /dev/null; then
    sudo apt install -y certbot python3-certbot-nginx
    echo -e "${GREEN}✓ Certbot установлен${NC}"
else
    echo -e "${GREEN}✓ Certbot уже установлен${NC}"
fi

echo ""
echo -e "${BLUE}Шаг 6: Получение SSL сертификата...${NC}"
echo -e "${YELLOW}Нажмите Enter для получения сертификата...${NC}"
read -r

sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN" --redirect || {
    echo -e "${RED}✗ Не удалось получить сертификат!${NC}"
    echo -e "${YELLOW}Проверьте DNS настройки и попробуйте позже:${NC}"
    echo "  sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
}

echo ""
echo -e "${BLUE}Шаг 7: Обновление .env файла...${NC}"
if [ -f .env ]; then
    if grep -q "WEBAPP_URL=" .env; then
        sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=https://$DOMAIN|g" .env
        echo -e "${GREEN}✓ WEBAPP_URL обновлен на https://$DOMAIN${NC}"
    else
        echo "WEBAPP_URL=https://$DOMAIN" >> .env
        echo -e "${GREEN}✓ WEBAPP_URL добавлен в .env${NC}"
    fi
fi

echo ""
echo -e "${BLUE}Шаг 8: Настройка firewall...${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable || true
echo -e "${GREEN}✓ Firewall настроен${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo -e "Настройка завершена!"
echo -e "==========================================${NC}"
echo ""
echo "Проверка: curl https://$DOMAIN/health"
SCRIPT_EOF

chmod +x setup_domain_onlyface.sh
echo "Скрипт создан! Запустите: ./setup_domain_onlyface.sh"
SERVER_SCRIPT

EOF

echo "Скопируйте и выполните команды выше на вашем компьютере"

