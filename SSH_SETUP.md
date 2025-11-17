# 🔐 Настройка SSH подключения к серверу

## Проблема: Permission denied (publickey)

Это означает, что SSH ключ не настроен или неверный.

## Решение:

### Вариант 1: Использовать существующий SSH ключ

**На вашем Mac проверьте наличие ключа:**

```bash
ls -la ~/.ssh/id_rsa.pub
```

**Если ключ есть, скопируйте его:**

```bash
cat ~/.ssh/id_rsa.pub
```

**Добавьте ключ в Яндекс.Облако:**

1. Откройте консоль Яндекс.Облака
2. Перейдите в **"Compute Cloud"** → **"Виртуальные машины"**
3. Откройте вашу ВМ `158.160.96.182`
4. Нажмите **"Редактировать"**
5. В разделе **"Доступ"** → **"SSH-ключ"**
6. Нажмите **"Добавить ключ"**
7. Вставьте содержимое `~/.ssh/id_rsa.pub`
8. Сохраните изменения

**Подключитесь:**

```bash
ssh ubuntu@158.160.96.182
```

### Вариант 2: Создать новый SSH ключ

**Создайте новый ключ:**

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# Нажмите Enter для всех вопросов (или укажите пароль)
```

**Скопируйте публичный ключ:**

```bash
cat ~/.ssh/id_rsa.pub
```

**Добавьте ключ в Яндекс.Облако** (см. Вариант 1)

**Подключитесь:**

```bash
ssh ubuntu@158.160.96.182
```

### Вариант 3: Использовать ключ с указанием пути

**Если ключ в другом месте:**

```bash
ssh -i ~/.ssh/your_key_name ubuntu@158.160.96.182
```

## После успешного подключения:

### 1. Скопируйте скрипт на сервер

**С вашего Mac:**

```bash
# Подключитесь к серверу
ssh ubuntu@158.160.96.182

# На сервере создайте директорию (если нет)
mkdir -p ~/facy-app
cd ~/facy-app

# Скопируйте скрипт с вашего Mac (в другом терминале на Mac):
# scp setup_web_cis.sh ubuntu@158.160.96.182:~/facy-app/
```

**Или создайте скрипт прямо на сервере:**

```bash
# На сервере выполните:
cd ~/facy-app
cat > setup_web_cis.sh << 'SCRIPTEOF'
#!/bin/bash
# Скрипт настройки веб-приложения для РФ/РБ

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

echo -e "${BLUE}🌐 Настройка веб-приложения для onlyface.art${NC}"
echo "======================================"
echo ""

DOMAIN="onlyface.art"

echo -e "${BLUE}📦 Установка Nginx...${NC}"
sudo apt update
sudo apt install -y nginx

echo ""
echo -e "${BLUE}🔧 Создание конфигурации Nginx...${NC}"

sudo tee /etc/nginx/sites-available/onlyface > /dev/null <<EOF
server {
    listen 80;
    server_name onlyface.art www.onlyface.art;

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
        alias /home/ubuntu/facy-app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /uploads/ {
        alias /home/ubuntu/facy-app/uploads/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    location /generated/ {
        alias /home/ubuntu/facy-app/generated/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/onlyface /etc/nginx/sites-enabled/
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
echo -e "${YELLOW}⚠️  Убедитесь, что DNS запись для onlyface.art указывает на 158.160.96.182${NC}"
echo -e "${YELLOW}Нажмите Enter когда DNS настроен, или Ctrl+C для отмены...${NC}"
read -r

echo ""
echo -e "${BLUE}🔐 Установка SSL сертификата (Let's Encrypt)...${NC}"
sudo apt install -y certbot python3-certbot-nginx

echo ""
echo -e "${BLUE}Получение SSL сертификата...${NC}"
sudo certbot --nginx -d onlyface.art -d www.onlyface.art --non-interactive --agree-tos --email admin@onlyface.art || {
    echo -e "${RED}❌ Не удалось получить сертификат!${NC}"
    echo -e "${YELLOW}Проверьте DNS настройки и попробуйте позже:${NC}"
    echo "sudo certbot --nginx -d onlyface.art"
    exit 1
}

if [ -f .env ]; then
    echo ""
    echo -e "${BLUE}Обновление WEBAPP_URL в .env...${NC}"
    sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=https://onlyface.art|g" .env
    echo -e "${GREEN}✅ WEBAPP_URL обновлен на https://onlyface.art${NC}"
fi

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
echo "  - HTTPS: https://onlyface.art"
echo "  - HTTP: http://onlyface.art"
echo "  - API Health: https://onlyface.art/health"
SCRIPTEOF

chmod +x setup_web_cis.sh
echo "✅ Скрипт создан!"
```

### 2. Запустите скрипт

```bash
cd ~/facy-app
./setup_web_cis.sh
```

## Альтернатива: Ручная настройка

Если скрипт не работает, выполните команды вручную (см. `DEPLOY_ONLYFACE_ART.md`)

