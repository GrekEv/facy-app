# ⚡ Быстрый старт: OnlyFace.art

## 🎯 За 10 минут

### Шаг 1: Создайте сервер (5 минут)

1. **Яндекс.Облако:** https://cloud.yandex.ru
2. **Compute Cloud** → **ВМ** → **Создать**
3. Настройки:
   - Ubuntu 22.04 LTS
   - 2 vCPU, 4 GB RAM, 20 GB SSD
   - Публичный IP: ✅
   - Скопируйте IP (например: `158.160.96.182`)

### Шаг 2: Создайте PostgreSQL (5 минут)

1. **Managed Databases** → **PostgreSQL** → **Создать**
2. Настройки:
   - Класс: `s2.micro` (от 500₽/мес)
   - БД: `onlyface_db`
   - Пользователь: `onlyface_user`
   - Пароль: (сохраните!)
   - Публичный доступ: ✅
3. Скопируйте хост (например: `c-xxxxx.rw.mdb.yandexcloud.net`)

### Шаг 3: Настройте DNS (2 минуты)

**В панели регистратора `onlyface.art`:**
- A запись: `@` → `158.160.96.182`
- A запись: `www` → `158.160.96.182`

### Шаг 4: Запустите на сервере (5 минут)

```bash
# Подключитесь к серверу
ssh ubuntu@158.160.96.182

# Установите Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Выйдите и войдите снова
exit
ssh ubuntu@158.160.96.182

# Клонируйте репозиторий
git clone https://github.com/GrekEv/facy-app.git
cd facy-app

# Создайте .env файл
cat > .env << 'EOF'
BOT_TOKEN=8374729179:AAG7wyo467ksUQgNyoESNzc09Wn0UBS7T7g
WEBAPP_URL=https://onlyface.art
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://onlyface_user:ВАШ_ПАРОЛЬ@c-xxxxx.rw.mdb.yandexcloud.net:6432/onlyface_db?ssl=require
HOST=0.0.0.0
PORT=8000
REPLICATE_API_KEY=your_replicate_api_key_here
REPLICATE_API_URL=https://api.replicate.com/v1
OPENAI_API_KEY=your_openai_api_key_here
SORA_MODEL=sora-1.0-pro
IMAGE_GENERATION_PROVIDER=replicate
VIDEO_GENERATION_PROVIDER=sora
EOF

# Замените ВАШ_ПАРОЛЬ и c-xxxxx на реальные значения
nano .env

# Исправьте все проблемы в коде (скопируйте команды из DEPLOY_COMPLETE.md раздел 3.4)

# Соберите и запустите
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# Установите Nginx и SSL
chmod +x setup_onlyface.sh
./setup_onlyface.sh
```

### Шаг 5: Настройте BotFather

1. Откройте @BotFather
2. `/mybots` → выберите бота
3. **Bot Settings** → **Menu Button**
4. **URL:** `https://onlyface.art`

## ✅ Готово!

- 🌐 Сайт: https://onlyface.art
- 🤖 Бот: работает в Telegram
- 📱 Mini App: через кнопку в боте

**Полная инструкция:** [DEPLOY_COMPLETE.md](DEPLOY_COMPLETE.md)

