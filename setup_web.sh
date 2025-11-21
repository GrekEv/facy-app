#!/bin/bash
# �к��пт дл� на�т�ойк� ве�-п��ложен�� � Nginx � HTTPS

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE} �а�т�ойка ве�-п��ложен��${NC}"
echo "================================"
echo ""

# ��ове�ка, что м� на �е�ве�е
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}  �е запу�кайте �к��пт от root. И�пол�зуйте о��чно�о пол�зовател�.${NC}"
    exit 1
fi

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

# Зап�о� домена
echo -e "${BLUE}�вед�те ваш домен (�л� нажм�те Enter дл� ��пол�зован�� IP):${NC}"
read -r DOMAIN

if [ -z "$DOMAIN" ]; then
    DOMAIN="158.160.96.182"
    USE_IP=true
    echo -e "${YELLOW}И�пол�зует�� IP ад�е�: $DOMAIN${NC}"
else
    USE_IP=false
    echo -e "${GREEN}И�пол�зует�� домен: $DOMAIN${NC}"
fi

echo ""
echo -e "${BLUE}� У�тановка Nginx...${NC}"
sudo apt update
sudo apt install -y nginx

echo ""
echo -e "${BLUE} �оздан�е конф��у�ац�� Nginx...${NC}"

# �оздаем конф��у�ац�� Nginx
sudo tee /etc/nginx/sites-available/facy > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    # Увел�чен�е �азме�а за��ужаем�� файлов
    client_max_body_size 100M;

    # О�новное п��ложен�е
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # �л� WebSocket (е�л� ��пол�зует��)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Таймаут�
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # �тат�че�к�е файл�
    location /static/ {
        alias $(pwd)/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # За��уженн�е файл�
    location /uploads/ {
        alias $(pwd)/uploads/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # ��ене���ованн�е файл�
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

# �кт�в��уем конф��у�ац��
sudo ln -sf /etc/nginx/sites-available/facy /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# ��ове��ем конф��у�ац��
echo ""
echo -e "${BLUE} ��ове�ка конф��у�ац�� Nginx...${NC}"
sudo nginx -t

# �е�езапу�каем Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo -e "${GREEN} Nginx на�т�оен!${NC}"

# �а�т�ойка SSL (тол�ко е�л� е�т� домен)
if [ "$USE_IP" = false ]; then
    echo ""
    echo -e "${BLUE} �а�т�ойка SSL �е�т�ф�ката...${NC}"
    echo -e "${YELLOW}У�ед�те��, что DNS зап��� дл� $DOMAIN указ�вает на IP: 158.160.96.182${NC}"
    echo -e "${YELLOW}�ажм�те Enter ко�да DNS �удет на�т�оен, �л� Ctrl+C дл� п�опу�ка...${NC}"
    read -r
    
    echo ""
    echo -e "${BLUE}У�тановка Certbot...${NC}"
    sudo apt install -y certbot python3-certbot-nginx
    
    echo ""
    echo -e "${BLUE}�олучен�е SSL �е�т�ф�ката...${NC}"
    sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email admin@$DOMAIN || {
        echo -e "${YELLOW}  �е удало�� получ�т� �е�т�ф�кат. ��ове��те DNS на�т�ойк�.${NC}"
        echo -e "${YELLOW}�� можете на�т�о�т� SSL позже командой:${NC}"
        echo "sudo certbot --nginx -d $DOMAIN"
    }
    
    # О�новл�ем WEBAPP_URL в .env
    if [ -f .env ]; then
        echo ""
        echo -e "${BLUE}О�новлен�е WEBAPP_URL в .env...${NC}"
        sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=https://$DOMAIN|g" .env
        echo -e "${GREEN} WEBAPP_URL о�новлен на https://$DOMAIN${NC}"
    fi
else
    echo ""
    echo -e "${YELLOW}  �л� Telegram Mini App т�е�ует�� HTTPS.${NC}"
    echo -e "${YELLOW}�екомендует�� на�т�о�т� домен � SSL �е�т�ф�кат.${NC}"
    echo ""
    echo -e "${BLUE}Теку��й URL: http://$DOMAIN${NC}"
    if [ -f .env ]; then
        sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=http://$DOMAIN|g" .env
    fi
fi

# �а�т�ойка firewall
echo ""
echo -e "${BLUE} �а�т�ойка firewall...${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable || true

echo ""
echo -e "${GREEN} �е�-п��ложен�е на�т�оено!${NC}"
echo ""
echo -e "${BLUE} Инфо�мац��:${NC}"
echo "  - HTTP: http://$DOMAIN"
if [ "$USE_IP" = false ]; then
    echo "  - HTTPS: https://$DOMAIN"
fi
echo "  - API Health: http://$DOMAIN/health"
echo ""
echo -e "${BLUE} �леду���е ша��:${NC}"
echo "1. О�нов�те WEBAPP_URL в BotFather:"
echo "   - Отк�ойте @BotFather"
echo "   - /mybots � в��е��те �ота"
echo "   - Bot Settings � Menu Button"
echo "   - URL: http://$DOMAIN (�л� https://$DOMAIN е�л� на�т�оен SSL)"
echo ""
echo "2. �е�езапу�т�те п��ложен�е:"
echo "   docker compose -f docker-compose.prod.yml restart"
echo ""
echo "3. ��ове��те �а�оту:"
echo "   curl http://$DOMAIN/health"





