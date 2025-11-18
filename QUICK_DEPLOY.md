# 🚀 Быстрое развертывание на сервере

## ✅ Вы уже подключены к серверу!

Теперь выполните команды на сервере:

## 📦 Шаг 1: Подготовка окружения

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv git curl

# Установка Docker
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    rm get-docker.sh
    echo "✅ Docker установлен. Перезайдите в систему: exit, затем ssh ubuntu@158.160.96.182"
    exit
fi

# Установка Docker Compose
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi
```

## 📥 Шаг 2: Клонирование проекта

```bash
# Перейдите в домашнюю директорию
cd ~

# Если проект уже есть, обновите его
if [ -d "facy-app" ]; then
    cd facy-app
    git pull || echo "Не удалось обновить через git"
else
    # Если проекта нет, создайте директорию
    mkdir -p facy-app
    cd facy-app
    echo "⚠️  Скопируйте файлы проекта в эту директорию"
fi
```

## ⚙️ Шаг 3: Создание .env файла

```bash
cd ~/facy-app

cat > .env << 'EOF'
BOT_TOKEN=8254778202:AAH-1RebJBOKpr5fKorcIcFHqKAihbCBQ_o
WEBAPP_URL=https://onlyface.art
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql+asyncpg://facy_user:etxX4gk272PdJYH@rc1a-6t9pb3se81b4idf5.mdb.yandexcloud.net:6432/facy_db?ssl=require
EOF

cat .env
```

## 📋 Шаг 4: Копирование файлов проекта

**С вашего Mac скопируйте файлы на сервер:**

```bash
# На вашем Mac выполните:
cd /Users/kirilldeniushkin/telegram-deepface-app
scp -r * ubuntu@158.160.96.182:~/facy-app/
```

**Или создайте файлы вручную на сервере** (если git не работает)

## 🐳 Шаг 5: Запуск через Docker

```bash
cd ~/facy-app

# Проверьте наличие docker-compose.prod.yml
ls -la docker-compose.prod.yml

# Если файл есть, запустите:
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Проверьте статус
docker compose -f docker-compose.prod.yml ps

# Просмотр логов
docker compose -f docker-compose.prod.yml logs -f
```

## 🔄 Шаг 6: Если Docker не установлен или не работает

**Используйте Python напрямую:**

```bash
cd ~/facy-app

# Установка зависимостей
pip3 install -r requirements.txt

# Запуск API в фоне
nohup python3 run_api.py > api.log 2>&1 &

# Запуск бота в фоне
nohup python3 main.py > bot.log 2>&1 &

# Проверка
ps aux | grep python3
curl http://localhost:8000/health
```

## ✅ Проверка работы

```bash
# Проверка API
curl http://localhost:8000/health

# Должно вернуть: {"status":"healthy"}
```

## 🌐 Шаг 7: Настройка Nginx и SSL

```bash
cd ~/facy-app
chmod +x setup_web_cis.sh
./setup_web_cis.sh
```

Или следуйте инструкции в `DEPLOY_ONLYFACE_ART.md`


