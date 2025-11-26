# Исправление проблем с сервером

## Где настраивать

**На сервере (через SSH)**, а НЕ в Timeweb или reg.ru.

Timeweb/reg.ru используются только для DNS записей (уже настроено).

## Быстрое решение

```bash
ssh root@72.56.85.215
cd ~/facy-app
./setup_domain_onlyface.sh
```

Этот скрипт автоматически:
- Настроит Nginx
- Получит SSL сертификат
- Запустит API
- Настроит firewall

## Ручная настройка

### 1. Проверка и запуск API

```bash
ssh root@72.56.85.215
cd ~/facy-app

# Определите команду docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
else
    COMPOSE="docker compose"
fi

# Запуск контейнеров
$COMPOSE -f docker-compose.prod.yml up -d

# Проверка
curl http://localhost:8000/health
```

### 2. Установка и настройка Nginx

```bash
# Установка (если не установлен)
sudo apt update
sudo apt install -y nginx

# Создание конфигурации
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

# Проверка конфигурации
sudo nginx -t

# Перезапуск
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 3. Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d onlyface.art -d www.onlyface.art --non-interactive --agree-tos --email admin@onlyface.art --redirect
```

### 4. Настройка Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

## Проверка

```bash
# На сервере
curl http://localhost:8000/health
curl http://localhost/health

# С вашего компьютера
curl http://onlyface.art/health
curl https://onlyface.art/health
```

## Проблемы

### Nginx не запускается

```bash
sudo nginx -t  # Проверка конфигурации
sudo systemctl status nginx  # Статус
sudo journalctl -u nginx -n 50  # Логи
```

### API не отвечает

```bash
cd ~/facy-app
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs api
```

### Firewall блокирует

```bash
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## Важно

- **Timeweb/reg.ru** - только для DNS (уже настроено)
- **Сервер** - здесь настраиваются Nginx, API, SSL, firewall
- Все настройки делаются через SSH на сервере

