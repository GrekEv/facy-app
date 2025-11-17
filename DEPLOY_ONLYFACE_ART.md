# 🚀 Развертывание на домене onlyface.art

## 📋 Текущая конфигурация:

- **Домен:** `onlyface.art`
- **WEBAPP_URL:** `https://onlyface.art` (уже обновлен в .env)
- **База данных:** PostgreSQL в Яндекс.Облаке
- **Хост БД:** `rc1a-6t9pb3se81b4idf5.mdb.yandexcloud.net`

## 🔧 Шаг 1: Настройка DNS

**В панели управления доменом (где зарегистрирован onlyface.art) добавьте A-запись:**

```
Тип: A
Имя: @ (или оставьте пустым для корневого домена)
Значение: 158.160.96.182  (IP вашей ВМ в Яндекс.Облаке)
TTL: 3600
```

**Также добавьте для www:**

```
Тип: A
Имя: www
Значение: 158.160.96.182
TTL: 3600
```

**Проверка DNS (после настройки подождите 5-15 минут):**

```bash
# Проверка A-записи
dig onlyface.art +short
# Должно вернуть: 158.160.96.182

# Проверка www
dig www.onlyface.art +short
# Должно вернуть: 158.160.96.182
```

## 🖥️ Шаг 2: Настройка на сервере

**Подключитесь к вашей ВМ в Яндекс.Облаке:**

```bash
ssh ubuntu@158.160.96.182
```

**Выполните скрипт автоматической настройки:**

```bash
cd ~/facy-app

# Скачайте или используйте готовый скрипт
chmod +x setup_web_cis.sh
./setup_web_cis.sh
```

**Или настройте вручную:**

### 2.1. Установка Nginx

```bash
sudo apt update
sudo apt install -y nginx
```

### 2.2. Создание конфигурации Nginx

```bash
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

# Активация
sudo ln -sf /etc/nginx/sites-available/onlyface /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Проверка конфигурации
sudo nginx -t

# Перезапуск Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 2.3. Установка SSL сертификата (Let's Encrypt)

**⚠️ Важно: Убедитесь, что DNS настроен и домен указывает на ваш IP!**

```bash
# Установка Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение SSL сертификата
sudo certbot --nginx -d onlyface.art -d www.onlyface.art --non-interactive --agree-tos --email admin@onlyface.art
```

**Если возникли проблемы:**

```bash
# Проверьте DNS
dig onlyface.art +short

# Попробуйте снова
sudo certbot --nginx -d onlyface.art -d www.onlyface.art
```

### 2.4. Обновление .env на сервере

```bash
cd ~/facy-app
nano .env
```

**Убедитесь, что указано:**

```env
BOT_TOKEN=8374729179:AAG7wyo467ksUQgNyoESNzc09Wn0UBS7T7g
WEBAPP_URL=https://onlyface.art
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql+asyncpg://facy_user:etxX4gk272PdJYH@rc1a-6t9pb3se81b4idf5.mdb.yandexcloud.net:6432/facy_db?ssl=require
```

### 2.5. Настройка Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### 2.6. Перезапуск приложения

```bash
cd ~/facy-app
docker compose -f docker-compose.prod.yml restart
```

**Или если используете Python напрямую:**

```bash
# Остановите старый процесс
pkill -f run_api.py
pkill -f main.py

# Запустите заново
cd ~/facy-app
python3 run_api.py &
python3 main.py &
```

## 🤖 Шаг 3: Настройка Telegram бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/mybots`
3. Выберите вашего бота
4. Выберите **"Bot Settings"** → **"Menu Button"**
5. Включите **"Menu Button"**
6. В поле **"URL"** введите: `https://onlyface.art`
7. Нажмите **"Save"**

## ✅ Проверка работы

**Проверьте доступность:**

```bash
# Health check
curl https://onlyface.art/health

# Должно вернуть: {"status":"healthy"}
```

**В браузере:**

- Откройте: `https://onlyface.art`
- Должна открыться главная страница приложения

**В Telegram:**

- Откройте бота
- Нажмите кнопку "🚀 Открыть приложение" (Menu Button)
- Должна открыться Web App

## 🔄 Автоматическое обновление SSL

Let's Encrypt сертификаты действительны 90 дней. Настройте автоматическое обновление:

```bash
# Проверка автоматического обновления
sudo certbot renew --dry-run

# Certbot автоматически настроит cron для обновления
```

## 📝 Полезные команды

**Проверка Nginx:**

```bash
sudo nginx -t
sudo systemctl status nginx
sudo systemctl restart nginx
```

**Проверка SSL:**

```bash
sudo certbot certificates
```

**Просмотр логов:**

```bash
# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Логи приложения
docker compose -f docker-compose.prod.yml logs -f
```

## 🐛 Решение проблем

### Проблема: DNS не резолвится

**Решение:**
- Проверьте A-запись в панели регистратора домена
- Подождите 15-30 минут для распространения DNS
- Проверьте: `dig onlyface.art +short`

### Проблема: SSL сертификат не выдается

**Решение:**
- Убедитесь, что DNS настроен правильно
- Проверьте, что порты 80 и 443 открыты в группах безопасности
- Попробуйте: `sudo certbot certonly --standalone -d onlyface.art`

### Проблема: 502 Bad Gateway

**Решение:**
- Проверьте, что приложение запущено: `curl http://localhost:8000/health`
- Проверьте логи Nginx: `sudo tail -f /var/log/nginx/error.log`
- Перезапустите приложение: `docker compose -f docker-compose.prod.yml restart`

## ✅ Готово!

Ваше приложение развернуто на домене `onlyface.art`!

- 🌐 **HTTPS:** https://onlyface.art
- 🔒 **SSL:** Настроен через Let's Encrypt
- 🤖 **Telegram Bot:** Готов к работе
- 🗄️ **База данных:** PostgreSQL в Яндекс.Облаке


