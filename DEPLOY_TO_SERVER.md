# 🚀 Развертывание на сервере Yandex Cloud (постоянная работа)

## 📋 Цель: Запустить приложение на сервере 158.160.96.182 на постоянной основе

## 🔧 Шаг 1: Подключение к серверу

```bash
ssh ubuntu@158.160.96.182
```

## 📦 Шаг 2: Подготовка окружения на сервере

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv git curl

# Установка Docker (если еще не установлен)
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
fi

# Установка Docker Compose (если еще не установлен)
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Перезайдите в систему для применения изменений группы docker
exit
# Затем подключитесь снова: ssh ubuntu@158.160.96.182
```

## 📥 Шаг 3: Клонирование/обновление проекта

```bash
# Если проект еще не склонирован
cd ~
git clone https://github.com/your-repo/facy-app.git facy-app
# Или если репозиторий приватный, используйте SSH или токен

# Если проект уже есть, обновите его
cd ~/facy-app
git pull origin main
```

## ⚙️ Шаг 4: Настройка .env файла

```bash
cd ~/facy-app

# Создайте .env файл
cat > .env << 'ENVEOF'
BOT_TOKEN=8374729179:AAG7wyo467ksUQgNyoESNzc09Wn0UBS7T7g
WEBAPP_URL=https://onlyface.art
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql+asyncpg://facy_user:etxX4gk272PdJYH@rc1a-6t9pb3se81b4idf5.mdb.yandexcloud.net:6432/facy_db?ssl=require
ENVEOF

# Проверьте содержимое
cat .env
```

## 🐳 Шаг 5: Запуск через Docker Compose (РЕКОМЕНДУЕТСЯ)

```bash
cd ~/facy-app

# Сборка образов
docker compose -f docker-compose.prod.yml build

# Запуск в фоновом режиме
docker compose -f docker-compose.prod.yml up -d

# Проверка статуса
docker compose -f docker-compose.prod.yml ps

# Просмотр логов
docker compose -f docker-compose.prod.yml logs -f
```

## 🔄 Шаг 6: Настройка автозапуска (systemd)

**Создайте сервис для API:**

```bash
sudo tee /etc/systemd/system/facy-api.service > /dev/null << 'SERVICEEOF'
[Unit]
Description=Facy API Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/facy-app
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /home/ubuntu/facy-app/run_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Создайте сервис для бота
sudo tee /etc/systemd/system/facy-bot.service > /dev/null << 'SERVICEEOF'
[Unit]
Description=Facy Telegram Bot Service
After=network.target facy-api.service
Requires=facy-api.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/facy-app
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /home/ubuntu/facy-app/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable facy-api.service
sudo systemctl enable facy-bot.service

# Запустите сервисы
sudo systemctl start facy-api.service
sudo systemctl start facy-bot.service

# Проверьте статус
sudo systemctl status facy-api.service
sudo systemctl status facy-bot.service
```

## ✅ Шаг 7: Проверка работы

```bash
# Проверка API
curl http://localhost:8000/health

# Проверка логов
sudo journalctl -u facy-api.service -f
sudo journalctl -u facy-bot.service -f

# Или если используете Docker
docker compose -f docker-compose.prod.yml logs -f
```

## 🌐 Шаг 8: Настройка Nginx и SSL (если еще не настроено)

```bash
cd ~/facy-app
./setup_web_cis.sh
```

Или следуйте инструкции в `DEPLOY_ONLYFACE_ART.md`

## 🔧 Полезные команды

**Управление сервисами:**

```bash
# Остановка
sudo systemctl stop facy-api.service
sudo systemctl stop facy-bot.service

# Запуск
sudo systemctl start facy-api.service
sudo systemctl start facy-bot.service

# Перезапуск
sudo systemctl restart facy-api.service
sudo systemctl restart facy-bot.service

# Статус
sudo systemctl status facy-api.service
sudo systemctl status facy-bot.service

# Логи
sudo journalctl -u facy-api.service -n 50
sudo journalctl -u facy-bot.service -n 50
```

**Управление Docker:**

```bash
# Остановка
docker compose -f docker-compose.prod.yml down

# Запуск
docker compose -f docker-compose.prod.yml up -d

# Перезапуск
docker compose -f docker-compose.prod.yml restart

# Логи
docker compose -f docker-compose.prod.yml logs -f

# Статус
docker compose -f docker-compose.prod.yml ps
```

## 🔄 Обновление приложения

```bash
cd ~/facy-app

# Обновить код
git pull origin main

# Пересобрать и перезапустить (Docker)
docker compose -f docker-compose.prod.yml up -d --build

# Или перезапустить сервисы (systemd)
sudo systemctl restart facy-api.service
sudo systemctl restart facy-bot.service
```

## ✅ Готово!

Теперь приложение работает на сервере постоянно и автоматически запускается при перезагрузке!


