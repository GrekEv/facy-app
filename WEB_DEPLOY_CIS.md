# 🌐 Развертывание веб-приложения для РФ и РБ

## 🎯 Решения для России и Беларуси

### Вариант 1: Яндекс.Облако + Российский домен (рекомендуется) ⭐

**Преимущества:**
- ✅ Полностью доступен в РФ и РБ
- ✅ SSL через Let's Encrypt (работает в РФ)
- ✅ Быстрая скорость
- ✅ Нет проблем с блокировками

**Что нужно:**
1. Домен на `.ru`, `.рф` или `.by` (регистраторы: reg.ru, nic.ru, timeweb.ru)
2. Сервер на Яндекс.Облаке (уже есть)
3. SSL через Let's Encrypt (бесплатно)

### Вариант 2: Cloudflare (альтернатива)

**⚠️ Внимание:** Cloudflare может быть заблокирован или медленно работать в РФ/РБ

**Если хотите использовать Cloudflare:**
- ✅ Бесплатный SSL
- ✅ CDN для ускорения
- ⚠️ Может быть заблокирован
- ⚠️ Может быть медленным в РФ

## 🚀 Быстрая настройка (Яндекс.Облако + Российский домен)

### Шаг 1: Регистрация домена

**Рекомендуемые регистраторы:**
- **reg.ru** - от 99₽/год
- **nic.ru** - от 199₽/год  
- **timeweb.ru** - от 149₽/год

**Выберите домен:**
- `.ru` - классический вариант
- `.рф` - кириллический домен
- `.by` - для Беларуси

### Шаг 2: Настройка DNS

**В панели регистратора домена добавьте A-запись:**

```
Тип: A
Имя: @ (или www)
Значение: 158.160.96.182
TTL: 3600
```

**Или используйте Yandex Cloud DNS:**

1. В консоли Яндекс.Облака: **Cloud DNS** → **Создать зону**
2. **Имя зоны:** `facy-zone`
3. **Домен:** `ваш-домен.ru`
4. **Тип:** Публичная
5. Скопируйте NS-серверы
6. В панели регистратора домена укажите эти NS-серверы
7. В зоне Cloud DNS создайте A-запись:
   - **Имя:** `@`
   - **Тип:** A
   - **Значение:** `158.160.96.182`

### Шаг 3: Установка Nginx и SSL

**На сервере выполните:**

```bash
cd ~/facy-app

# Установка Nginx
sudo apt update
sudo apt install -y nginx

# Создание конфигурации
sudo tee /etc/nginx/sites-available/facy > /dev/null <<'EOF'
server {
    listen 80;
    server_name ваш-домен.ru www.ваш-домен.ru;

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
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
    }
    
    location /generated/ {
        alias /home/ubuntu/facy-app/generated/;
        expires 7d;
    }
}
EOF

# Замените ваш-домен.ru на ваш домен
sudo sed -i "s/ваш-домен.ru/ВАШ_ДОМЕН.ru/g" /etc/nginx/sites-available/facy

# Активация
sudo ln -sf /etc/nginx/sites-available/facy /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Установка SSL
sudo apt install -y certbot python3-certbot-nginx

# Получение сертификата (замените на ваш домен)
sudo certbot --nginx -d ваш-домен.ru -d www.ваш-домен.ru --non-interactive --agree-tos --email admin@ваш-домен.ru

# Обновление .env
sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=https://ваш-домен.ru|g" .env

# Перезапуск приложения
docker compose -f docker-compose.prod.yml restart
```

### Шаг 4: Настройка Telegram Bot

1. Откройте [@BotFather](https://t.me/BotFather)
2. `/mybots` → выберите бота
3. **Bot Settings** → **Menu Button**
4. **URL:** `https://ваш-домен.ru`

## 🔄 Альтернатива: Cloudflare (если нужно)

### Настройка Cloudflare

**⚠️ Проверьте доступность Cloudflare в вашем регионе!**

1. **Регистрация на Cloudflare:**
   - Откройте https://cloudflare.com
   - Зарегистрируйтесь (бесплатно)

2. **Добавление домена:**
   - Добавьте ваш домен
   - Cloudflare автоматически найдет DNS записи
   - Измените NS-серверы в панели регистратора на те, что дал Cloudflare

3. **Настройка DNS в Cloudflare:**
   - Добавьте A-запись: `@` → `158.160.96.182`
   - Добавьте A-запись: `www` → `158.160.96.182`

4. **Настройка SSL:**
   - В Cloudflare: **SSL/TLS** → **Overview**
   - Выберите **Flexible** (если нет SSL на сервере) или **Full** (если есть SSL)
   - Cloudflare автоматически выдаст SSL сертификат

5. **Настройка на сервере:**
   - Если используете Cloudflare, можно не устанавливать SSL на сервере
   - Nginx будет работать на HTTP (порт 80)
   - Cloudflare будет проксировать HTTPS

**Обновление .env:**
```bash
WEBAPP_URL=https://ваш-домен.ru
```

## 📋 Автоматический скрипт для РФ/РБ

Создайте файл `setup_web_cis.sh`:

```bash
#!/bin/bash
# Скрипт настройки веб-приложения для РФ/РБ

set -e

cd ~/facy-app || exit 1

echo "🌐 Настройка веб-приложения для РФ/РБ"
echo "======================================"
echo ""

# Запрос домена
read -p "Введите ваш домен (например: facy-app.ru): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo "❌ Домен обязателен для Telegram Mini App!"
    exit 1
fi

echo ""
echo "📦 Установка Nginx..."
sudo apt update
sudo apt install -y nginx

echo ""
echo "🔧 Создание конфигурации Nginx..."

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
    }

    location /static/ {
        alias $(pwd)/static/;
        expires 30d;
    }
    
    location /uploads/ {
        alias $(pwd)/uploads/;
        expires 7d;
    }
    
    location /generated/ {
        alias $(pwd)/generated/;
        expires 7d;
    }
}
EOF

# Активация
sudo ln -sf /etc/nginx/sites-available/facy /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo "🔐 Установка SSL сертификата..."
echo "⚠️  Убедитесь, что DNS запись для $DOMAIN указывает на 158.160.96.182"
read -p "Нажмите Enter когда DNS настроен..."

sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Обновление .env
if [ -f .env ]; then
    sed -i "s|WEBAPP_URL=.*|WEBAPP_URL=https://$DOMAIN|g" .env
    echo "✅ WEBAPP_URL обновлен в .env"
fi

# Настройка firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable || true

echo ""
echo "✅ Готово!"
echo ""
echo "📋 Информация:"
echo "  - HTTPS: https://$DOMAIN"
echo "  - API Health: https://$DOMAIN/health"
echo ""
echo "📝 Следующие шаги:"
echo "1. Настройте Menu Button в BotFather:"
echo "   URL: https://$DOMAIN"
echo ""
echo "2. Перезапустите приложение:"
echo "   docker compose -f docker-compose.prod.yml restart"
```

## ✅ Проверка работы

```bash
# Проверка HTTP
curl http://ваш-домен.ru/health

# Проверка HTTPS
curl https://ваш-домен.ru/health

# Проверка в браузере
# Откройте: https://ваш-домен.ru
```

## 🐛 Решение проблем

### Проблема: DNS не резолвится

```bash
# Проверьте DNS
dig ваш-домен.ru
nslookup ваш-домен.ru

# Проверьте настройки DNS в панели регистратора
```

### Проблема: SSL не устанавливается

```bash
# Проверьте, что порты 80 и 443 открыты
sudo ufw status

# Проверьте логи Certbot
sudo certbot certificates

# Попробуйте вручную
sudo certbot --nginx -d ваш-домен.ru --debug
```

### Проблема: Cloudflare не работает

Если Cloudflare заблокирован или медленный:
1. Используйте вариант с Let's Encrypt напрямую
2. Или используйте российский CDN (Yandex CDN)

## 💡 Рекомендации для РФ/РБ

1. **Используйте российские домены** (.ru, .рф) - быстрее и надежнее
2. **Let's Encrypt работает в РФ** - можно использовать бесплатный SSL
3. **Яндекс.Облако** - лучший выбор для хостинга
4. **Избегайте Cloudflare** если есть проблемы с доступностью

## 🎉 Готово!

После настройки ваше приложение будет доступно:
- Как веб-сайт: `https://ваш-домен.ru`
- Как Telegram Mini App: через кнопку в боте

**Важно:** Telegram Mini App требует HTTPS, поэтому SSL обязателен!

