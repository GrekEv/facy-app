#!/bin/bash
# �к��пт на�т�ойк� ве�-п��ложен�� дл� onlyface.art

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

DOMAIN="onlyface.art"

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

echo -e "${BLUE} �а�т�ойка ве�-п��ложен�� дл� $DOMAIN${NC}"
echo "=========================================="
echo ""

echo -e "${YELLOW}  У�ед�те��, что DNS зап��� дл� $DOMAIN указ�вает на 158.160.96.182${NC}"
echo -e "${YELLOW}�ажм�те Enter ко�да DNS на�т�оен, �л� Ctrl+C дл� отмен�...${NC}"
read -r

echo ""
echo -e "${BLUE}� У�тановка Nginx...${NC}"
sudo apt update
sudo apt install -y nginx

echo ""
echo -e "${BLUE} �оздан�е конф��у�ац�� Nginx...${NC}"

# �оздаем конф��у�ац��
sudo tee /etc/nginx/sites-available/onlyface > /dev/null <<EOF
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

# �кт�вац��
sudo ln -sf /etc/nginx/sites-available/onlyface /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo ""
echo -e "${BLUE} ��ове�ка конф��у�ац��...${NC}"
sudo nginx -t

echo ""
echo -e "${BLUE}� �е�езапу�к Nginx...${NC}"
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo -e "${GREEN} Nginx на�т�оен!${NC}"

echo ""
echo -e "${BLUE} У�тановка SSL �е�т�ф�ката (Let's Encrypt)...${NC}"
sudo apt install -y certbot python3-certbot-nginx

echo ""
echo -e "${BLUE}�олучен�е SSL �е�т�ф�ката...${NC}"
sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN" || {
    echo -e "${RED} �е удало�� получ�т� �е�т�ф�кат!${NC}"
    echo -e "${YELLOW}��ове��те DNS на�т�ойк� � поп�о�уйте позже:${NC}"
    echo "sudo certbot --nginx -d $DOMAIN"
    exit 1
}

# О�новлен�е .env
if [ -f .env ]; then
    echo ""
    echo -e "${BLUE}О�новлен�е WEBAPP_URL в .env...${NC}"
    sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=https://$DOMAIN|g" .env
    echo -e "${GREEN} WEBAPP_URL о�новлен на https://$DOMAIN${NC}"
else
    echo ""
    echo -e "${YELLOW}  Файл .env не найден. �оздайте е�о в�учну�.${NC}"
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
echo "  - HTTPS: https://$DOMAIN"
echo "  - HTTP: http://$DOMAIN"
echo "  - API Health: https://$DOMAIN/health"
echo ""
echo -e "${BLUE} �леду���е ша��:${NC}"
echo "1. �а�т�ойте Menu Button в BotFather:"
echo "   - Отк�ойте @BotFather"
echo "   - /mybots � в��е��те �ота"
echo "   - Bot Settings � Menu Button"
echo "   - URL: https://$DOMAIN"
echo ""
echo "2. �е�езапу�т�те п��ложен�е:"
echo "   docker compose -f docker-compose.prod.yml restart"
echo ""
echo "3. ��ове��те �а�оту:"
echo "   curl https://$DOMAIN/health"
echo ""
echo -e "${GREEN} �отово! �аше п��ложен�е до�тупно на https://$DOMAIN${NC}"


