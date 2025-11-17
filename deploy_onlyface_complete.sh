#!/bin/bash
# Полный скрипт развертывания OnlyFace.art
# Включает все исправления и настройки

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

DOMAIN="onlyface.art"

echo -e "${BLUE}🚀 Полное развертывание OnlyFace.art${NC}"
echo "=========================================="
echo ""

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

echo -e "${BLUE}📋 Шаг 1: Исправление всех проблем в коде...${NC}"

# 1. Config.py - ENVIRONMENT
if ! grep -q "ENVIRONMENT: str" config.py; then
    echo "  ✓ Добавляю ENVIRONMENT..."
    sed -i '/WEBAPP_URL: str/a\    \n    # Environment\n    ENVIRONMENT: str = "production"  # development, production' config.py
fi

# 2. Config.py - extra = "ignore"
if ! grep -q 'extra = "ignore"' config.py; then
    echo "  ✓ Добавляю extra = ignore..."
    sed -i '/case_sensitive = True/a\        extra = "ignore"  # Игнорировать дополнительные поля из .env' config.py
fi

# 3. api/main.py - импорты
echo "  ✓ Исправляю импорты в api/main.py..."
sed -i 's/from \.schemas import/from api.schemas import/g' api/main.py
sed -i 's/from \. import payments/from api import payments/g' api/main.py

# 4. docker-compose.yml - удаляем version
sed -i '/^version:/d' docker-compose.yml

# 5. models.py - DeclarativeBase
if grep -q "declarative_base" database/models.py; then
    echo "  ✓ Обновляю Base на DeclarativeBase..."
    sed -i 's/from sqlalchemy.ext.declarative import declarative_base/from sqlalchemy.orm import DeclarativeBase, relationship/g' database/models.py
    sed -i 's/^Base = declarative_base()$/class Base(DeclarativeBase):\n    """Базовый класс для всех моделей"""\n    pass/g' database/models.py
fi

# 6. КРИТИЧЕСКОЕ: metadata -> transaction_metadata
if grep -q "^    metadata = Column" database/models.py; then
    echo "  ✓ Исправляю metadata -> transaction_metadata..."
    sed -i 's/^    metadata = Column(Text, nullable=True)/    transaction_metadata = Column(Text, nullable=True)/g' database/models.py
fi

# 7. docker-compose.prod.yml - healthcheck
if ! grep -q "start_period" docker-compose.prod.yml; then
    echo "  ✓ Обновляю healthcheck..."
    sed -i '/retries: 3$/a\      start_period: 40s' docker-compose.prod.yml 2>/dev/null || sed -i '/retries: 5$/a\      start_period: 40s' docker-compose.prod.yml
    sed -i 's/retries: 3/retries: 5/g' docker-compose.prod.yml
fi

echo -e "${GREEN}✅ Все файлы исправлены!${NC}"

echo ""
echo -e "${BLUE}📋 Шаг 2: Проверка .env файла...${NC}"

if [ ! -f .env ]; then
    echo -e "${RED}❌ Файл .env не найден!${NC}"
    echo -e "${YELLOW}Создайте файл .env с необходимыми переменными (см. DEPLOY_COMPLETE.md)${NC}"
    exit 1
fi

# Проверяем наличие обязательных переменных
if ! grep -q "BOT_TOKEN=" .env; then
    echo -e "${RED}❌ BOT_TOKEN не найден в .env!${NC}"
    exit 1
fi

if ! grep -q "DATABASE_URL=" .env; then
    echo -e "${RED}❌ DATABASE_URL не найден в .env!${NC}"
    exit 1
fi

# Обновляем WEBAPP_URL если нужно
if ! grep -q "WEBAPP_URL=https://$DOMAIN" .env; then
    echo "  ✓ Обновляю WEBAPP_URL на https://$DOMAIN..."
    sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=https://$DOMAIN|g" .env
fi

echo -e "${GREEN}✅ .env файл проверен!${NC}"

echo ""
echo -e "${BLUE}📋 Шаг 3: Сборка Docker образов...${NC}"
docker compose -f docker-compose.prod.yml build --no-cache

echo ""
echo -e "${BLUE}📋 Шаг 4: Запуск приложения...${NC}"
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
docker compose -f docker-compose.prod.yml up -d

echo ""
echo -e "${BLUE}⏳ Ожидание запуска (30 секунд)...${NC}"
sleep 30

echo ""
echo -e "${BLUE}📊 Проверка статуса контейнеров...${NC}"
docker compose -f docker-compose.prod.yml ps

echo ""
echo -e "${BLUE}📋 Проверка логов API...${NC}"
docker compose -f docker-compose.prod.yml logs api --tail=30

echo ""
echo -e "${BLUE}🔍 Проверка health endpoint...${NC}"
sleep 5
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API работает!${NC}"
else
    echo -e "${YELLOW}⚠️  API еще запускается или есть проблемы${NC}"
    echo -e "${YELLOW}Проверьте логи: docker compose -f docker-compose.prod.yml logs api${NC}"
fi

echo ""
echo -e "${BLUE}📋 Шаг 5: Настройка Nginx и SSL...${NC}"
echo -e "${YELLOW}⚠️  Убедитесь, что DNS для $DOMAIN настроен и указывает на ваш IP!${NC}"
read -p "Нажмите Enter когда DNS настроен, или Ctrl+C для пропуска..."

# Установка Nginx
if ! command -v nginx &> /dev/null; then
    echo "  ✓ Установка Nginx..."
    sudo apt update
    sudo apt install -y nginx
fi

# Создание конфигурации Nginx
echo "  ✓ Создание конфигурации Nginx..."
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

# Активация
sudo ln -sf /etc/nginx/sites-available/onlyface /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo -e "${GREEN}✅ Nginx настроен!${NC}"

# Установка SSL
if ! command -v certbot &> /dev/null; then
    echo "  ✓ Установка Certbot..."
    sudo apt install -y certbot python3-certbot-nginx
fi

echo "  ✓ Получение SSL сертификата..."
sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN" || {
    echo -e "${YELLOW}⚠️  Не удалось получить сертификат. Проверьте DNS и попробуйте позже:${NC}"
    echo "sudo certbot --nginx -d $DOMAIN"
}

# Настройка firewall
echo "  ✓ Настройка firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable || true

echo ""
echo -e "${GREEN}✅ Развертывание завершено!${NC}"
echo ""
echo -e "${BLUE}📋 Информация:${NC}"
echo "  - Веб-сайт: https://$DOMAIN"
echo "  - API Health: https://$DOMAIN/health"
echo "  - Статус контейнеров: docker compose -f docker-compose.prod.yml ps"
echo "  - Логи: docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo -e "${BLUE}📝 Следующие шаги:${NC}"
echo "1. Настройте Menu Button в BotFather:"
echo "   URL: https://$DOMAIN"
echo ""
echo "2. Проверьте работу:"
echo "   curl https://$DOMAIN/health"
echo ""
echo -e "${GREEN}🎉 Готово! OnlyFace.art развернут!${NC}"

