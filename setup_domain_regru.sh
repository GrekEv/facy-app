#!/bin/bash
# �к��пт автомат�че�кой на�т�ойк� домена � reg.ru

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE} �а�т�ойка домена дл� п��ложен��${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# ��ове�ка, что �к��пт запу�ен на �е�ве�е
if [ ! -d "/home/ubuntu" ]; then
    echo -e "${RED} �тот �к��пт должен ��т� запу�ен на �е�ве�е!${NC}"
    echo "�одкл�ч�те�� к �е�ве�у: ssh ubuntu@158.160.96.182"
    exit 1
fi

# Зап�о� домена
echo -e "${BLUE}�вед�те ваш домен (нап��ме�: example.ru):${NC}"
read -r DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED} �омен не указан!${NC}"
    exit 1
fi

# У���аем п�отокол � �леш� �з домена
DOMAIN=$(echo "$DOMAIN" | sed 's|^https\?://||' | sed 's|/$||' | sed 's|^www\.||')
# Е�л� домен нач�нает�� � www, о�тавл�ем тол�ко �ез www (www �удет до�авлен отдел�но)
DOMAIN_BASE="$DOMAIN"

# Зап�о� email дл� SSL
echo -e "${BLUE}�вед�те ваш email дл� SSL �е�т�ф�ката:${NC}"
read -r EMAIL

if [ -z "$EMAIL" ]; then
    echo -e "${YELLOW}  Email не указан, �удет ��пол�зован admin@$DOMAIN_BASE${NC}"
    EMAIL="admin@$DOMAIN_BASE"
fi

echo ""
echo -e "${BLUE} �а�т�ойк�:${NC}"
echo -e "  �омен: ${GREEN}$DOMAIN_BASE${NC}"
echo -e "  Email: ${GREEN}$EMAIL${NC}"
echo -e "  IP �е�ве�а: ${GREEN}158.160.96.182${NC}"
echo ""

echo -e "${YELLOW}  ��Ж�О: �е�ед п�одолжен�ем на�т�ойте DNS зап��� на reg.ru!${NC}"
echo -e "${YELLOW}   �о�ав�те A-зап��� дл� $DOMAIN_BASE � 158.160.96.182${NC}"
echo -e "${YELLOW}   �о�ав�те A-зап��� дл� www.$DOMAIN_BASE � 158.160.96.182${NC}"
echo ""
read -p "�ажм�те Enter ко�да DNS на�т�оен, �л� Ctrl+C дл� отмен�..."

echo ""
echo -e "${BLUE}� У�тановка Nginx...${NC}"
sudo apt update
sudo apt install -y nginx

echo ""
echo -e "${BLUE} �оздан�е конф��у�ац�� Nginx...${NC}"
cd ~/facy-app || {
    echo -e "${RED} ���екто��� ~/facy-app не найдена!${NC}"
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

# �кт�вац��
sudo ln -sf /etc/nginx/sites-available/facy /etc/nginx/sites-enabled/
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
echo -e "${BLUE} ��ове�ка DNS...${NC}"
echo -e "${YELLOW}��ове���, что домен указ�вает на �е�ве�...${NC}"

# ��ове�ка DNS
DNS_IP=$(dig +short $DOMAIN_BASE | tail -1)
if [ "$DNS_IP" = "158.160.96.182" ]; then
    echo -e "${GREEN} DNS на�т�оен п�ав�л�но!${NC}"
else
    echo -e "${YELLOW}  DNS е�е не на�т�оен �л� не �а�п�о�т�ан�л��${NC}"
    echo -e "${YELLOW}   Теку��й IP: $DNS_IP${NC}"
    echo -e "${YELLOW}   Ож�даем�й IP: 158.160.96.182${NC}"
    echo ""
    read -p "��одолж�т� у�тановку SSL? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}У�тановка SSL отменена. �а�т�ойте DNS � запу�т�те �к��пт �нова.${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE} У�тановка SSL �е�т�ф�ката (Let's Encrypt)...${NC}"
sudo apt install -y certbot python3-certbot-nginx

echo ""
echo -e "${BLUE}�олучен�е SSL �е�т�ф�ката...${NC}"
sudo certbot --nginx -d "$DOMAIN_BASE" -d "www.$DOMAIN_BASE" \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --redirect || {
    echo -e "${YELLOW}  �втомат�че�ка� у�тановка SSL не удала��${NC}"
    echo -e "${YELLOW}�оп�о�уйте у�танов�т� в�учну�:${NC}"
    echo "sudo certbot --nginx -d $DOMAIN_BASE -d www.$DOMAIN_BASE"
    exit 1
}

echo ""
echo -e "${GREEN} SSL �е�т�ф�кат у�тановлен!${NC}"

# О�новлен�е .env
echo ""
echo -e "${BLUE} О�новлен�е конф��у�ац�� п��ложен��...${NC}"
if [ -f .env ]; then
    if grep -q "WEBAPP_URL=" .env; then
        sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=https://$DOMAIN_BASE|g" .env
        echo -e "${GREEN} WEBAPP_URL о�новлен на https://$DOMAIN_BASE${NC}"
    else
        echo "WEBAPP_URL=https://$DOMAIN_BASE" >> .env
        echo -e "${GREEN} WEBAPP_URL до�авлен в .env${NC}"
    fi
else
    echo -e "${YELLOW}  Файл .env не найден${NC}"
fi

# �а�т�ойка firewall
echo ""
echo -e "${BLUE} �а�т�ойка firewall...${NC}"
sudo ufw allow 22/tcp 2>/dev/null || true
sudo ufw allow 80/tcp 2>/dev/null || true
sudo ufw allow 443/tcp 2>/dev/null || true
sudo ufw --force enable 2>/dev/null || true

echo ""
echo -e "${GREEN} �отово!${NC}"
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN} �омен на�т�оен!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${BLUE} Инфо�мац��:${NC}"
echo -e "  - HTTPS: ${GREEN}https://$DOMAIN_BASE${NC}"
echo -e "  - HTTP: ${GREEN}http://$DOMAIN_BASE${NC}"
echo -e "  - API Health: ${GREEN}https://$DOMAIN_BASE/health${NC}"
echo ""
echo -e "${BLUE} �леду���е ша��:${NC}"
echo -e "1. �а�т�ойте Menu Button в BotFather:"
echo -e "   - Отк�ойте @BotFather"
echo -e "   - /mybots � в��е��те �ота � Bot Settings � Menu Button"
echo -e "   - URL: ${GREEN}https://$DOMAIN_BASE${NC}"
echo ""
echo -e "2. �е�езапу�т�те п��ложен�е:"
echo -e "   ${GREEN}docker compose -f docker-compose.prod.yml restart${NC}"
echo ""
echo -e "3. ��ове��те �а�оту:"
echo -e "   ${GREEN}curl https://$DOMAIN_BASE/health${NC}"
echo ""
echo -e "${GREEN} �аше п��ложен�е до�тупно на https://$DOMAIN_BASE${NC}"

