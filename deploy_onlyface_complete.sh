#!/bin/bash
# �олн�й �к��пт �азве�т�ван�� OnlyFace.art
# �кл�чает в�е ��п�авлен�� � на�т�ойк�

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

DOMAIN="onlyface.art"

echo -e "${BLUE} �олное �азве�т�ван�е OnlyFace.art${NC}"
echo "=========================================="
echo ""

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

echo -e "${BLUE} �а� 1: И�п�авлен�е в�е� п�о�лем в коде...${NC}"

# 1. Config.py - ENVIRONMENT
if ! grep -q "ENVIRONMENT: str" config.py; then
    echo "   �о�авл�� ENVIRONMENT..."
    sed -i '/WEBAPP_URL: str/a\    \n    # Environment\n    ENVIRONMENT: str = "production"  # development, production' config.py
fi

# 2. Config.py - extra = "ignore"
if ! grep -q 'extra = "ignore"' config.py; then
    echo "   �о�авл�� extra = ignore..."
    sed -i '/case_sensitive = True/a\        extra = "ignore"  # И�но���оват� дополн�тел�н�е пол� �з .env' config.py
fi

# 3. api/main.py - �мпо�т�
echo "   И�п�авл�� �мпо�т� в api/main.py..."
sed -i 's/from \.schemas import/from api.schemas import/g' api/main.py
sed -i 's/from \. import payments/from api import payments/g' api/main.py

# 4. docker-compose.yml - удал�ем version
sed -i '/^version:/d' docker-compose.yml

# 5. models.py - DeclarativeBase
if grep -q "declarative_base" database/models.py; then
    echo "   О�новл�� Base на DeclarativeBase..."
    sed -i 's/from sqlalchemy.ext.declarative import declarative_base/from sqlalchemy.orm import DeclarativeBase, relationship/g' database/models.py
    sed -i 's/^Base = declarative_base()$/class Base(DeclarativeBase):\n    """Базов�й кла�� дл� в�е� моделей"""\n    pass/g' database/models.py
fi

# 6. ��ИТИ�Е��ОЕ: metadata -> transaction_metadata
if grep -q "^    metadata = Column" database/models.py; then
    echo "   И�п�авл�� metadata -> transaction_metadata..."
    sed -i 's/^    metadata = Column(Text, nullable=True)/    transaction_metadata = Column(Text, nullable=True)/g' database/models.py
fi

# 7. docker-compose.prod.yml - healthcheck
if ! grep -q "start_period" docker-compose.prod.yml; then
    echo "   О�новл�� healthcheck..."
    sed -i '/retries: 3$/a\      start_period: 40s' docker-compose.prod.yml 2>/dev/null || sed -i '/retries: 5$/a\      start_period: 40s' docker-compose.prod.yml
    sed -i 's/retries: 3/retries: 5/g' docker-compose.prod.yml
fi

echo -e "${GREEN} ��е файл� ��п�авлен�!${NC}"

echo ""
echo -e "${BLUE} �а� 2: ��ове�ка .env файла...${NC}"

if [ ! -f .env ]; then
    echo -e "${RED} Файл .env не найден!${NC}"
    echo -e "${YELLOW}�оздайте файл .env � нео��од�м�м� пе�еменн�м� (�м. DEPLOY_COMPLETE.md)${NC}"
    exit 1
fi

# ��ове��ем нал�ч�е о��зател�н�� пе�еменн��
if ! grep -q "BOT_TOKEN=" .env; then
    echo -e "${RED} BOT_TOKEN не найден в .env!${NC}"
    exit 1
fi

if ! grep -q "DATABASE_URL=" .env; then
    echo -e "${RED} DATABASE_URL не найден в .env!${NC}"
    exit 1
fi

# О�новл�ем WEBAPP_URL е�л� нужно
if ! grep -q "WEBAPP_URL=https://$DOMAIN" .env; then
    echo "   О�новл�� WEBAPP_URL на https://$DOMAIN..."
    sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=https://$DOMAIN|g" .env
fi

echo -e "${GREEN} .env файл п�ове�ен!${NC}"

echo ""
echo -e "${BLUE} �а� 3: ��о�ка Docker о��азов...${NC}"
docker compose -f docker-compose.prod.yml build --no-cache

echo ""
echo -e "${BLUE} �а� 4: Запу�к п��ложен��...${NC}"
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
docker compose -f docker-compose.prod.yml up -d

echo ""
echo -e "${BLUE} Ож�дан�е запу�ка (30 �екунд)...${NC}"
sleep 30

echo ""
echo -e "${BLUE} ��ове�ка �тату�а контейне�ов...${NC}"
docker compose -f docker-compose.prod.yml ps

echo ""
echo -e "${BLUE} ��ове�ка ло�ов API...${NC}"
docker compose -f docker-compose.prod.yml logs api --tail=30

echo ""
echo -e "${BLUE} ��ове�ка health endpoint...${NC}"
sleep 5
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN} API �а�отает!${NC}"
else
    echo -e "${YELLOW}  API е�е запу�кает�� �л� е�т� п�о�лем�${NC}"
    echo -e "${YELLOW}��ове��те ло��: docker compose -f docker-compose.prod.yml logs api${NC}"
fi

echo ""
echo -e "${BLUE} �а� 5: �а�т�ойка Nginx � SSL...${NC}"
echo -e "${YELLOW}  У�ед�те��, что DNS дл� $DOMAIN на�т�оен � указ�вает на ваш IP!${NC}"
read -p "�ажм�те Enter ко�да DNS на�т�оен, �л� Ctrl+C дл� п�опу�ка..."

# У�тановка Nginx
if ! command -v nginx &> /dev/null; then
    echo "   У�тановка Nginx..."
    sudo apt update
    sudo apt install -y nginx
fi

# �оздан�е конф��у�ац�� Nginx
echo "   �оздан�е конф��у�ац�� Nginx..."
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
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo -e "${GREEN} Nginx на�т�оен!${NC}"

# У�тановка SSL
if ! command -v certbot &> /dev/null; then
    echo "   У�тановка Certbot..."
    sudo apt install -y certbot python3-certbot-nginx
fi

echo "   �олучен�е SSL �е�т�ф�ката..."
sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN" || {
    echo -e "${YELLOW}  �е удало�� получ�т� �е�т�ф�кат. ��ове��те DNS � поп�о�уйте позже:${NC}"
    echo "sudo certbot --nginx -d $DOMAIN"
}

# �а�т�ойка firewall
echo "   �а�т�ойка firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable || true

echo ""
echo -e "${GREEN} �азве�т�ван�е заве�шено!${NC}"
echo ""
echo -e "${BLUE} Инфо�мац��:${NC}"
echo "  - �е�-�айт: https://$DOMAIN"
echo "  - API Health: https://$DOMAIN/health"
echo "  - �тату� контейне�ов: docker compose -f docker-compose.prod.yml ps"
echo "  - Ло��: docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo -e "${BLUE} �леду���е ша��:${NC}"
echo "1. �а�т�ойте Menu Button в BotFather:"
echo "   URL: https://$DOMAIN"
echo ""
echo "2. ��ове��те �а�оту:"
echo "   curl https://$DOMAIN/health"
echo ""
echo -e "${GREEN} �отово! OnlyFace.art �азве�нут!${NC}"



