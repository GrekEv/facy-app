# Полная инструкция по развертыванию OnlyFace

## Требования

- Сервер с Ubuntu 24.04
- Docker и Docker Compose
- Домен (например, onlyface.art)
- Telegram Bot Token

## Шаг 1: Подготовка сервера

```bash
ssh root@72.56.85.215
```

## Шаг 2: Клонирование репозитория

```bash
cd ~
git clone https://github.com/GrekEv/facy-app.git facy-app
cd facy-app
```

## Шаг 3: Настройка переменных окружения

```bash
cp ENV_EXAMPLE.txt .env
nano .env
```

Заполните обязательные переменные:
- `BOT_TOKEN` - токен Telegram бота
- `WEBAPP_URL` - URL веб-приложения (https://onlyface.art)
- `DATABASE_URL` - URL базы данных
- `DEEPFACE_API_KEY` - ключ API для deepfake
- `REPLICATE_API_KEY` - ключ для генерации изображений

## Шаг 4: Настройка DNS

1. В Timeweb: "Домены и SSL" → onlyface.art → DNS-записи
2. Добавьте A-записи:
   - @ → 72.56.85.215
   - www → 72.56.85.215

Подождите 5-15 минут для распространения DNS.

## Шаг 5: Настройка сервера

```bash
cd ~/facy-app
wget https://raw.githubusercontent.com/GrekEv/facy-app/main/setup_domain_onlyface.sh
chmod +x setup_domain_onlyface.sh
./setup_domain_onlyface.sh
```

Скрипт автоматически:
- Установит Nginx
- Настроит конфигурацию для домена
- Получит SSL сертификат
- Настроит firewall

## Шаг 6: Запуск приложения

```bash
cd ~/facy-app

# Определите команду docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
else
    COMPOSE="docker compose"
fi

# Запуск
$COMPOSE -f docker-compose.prod.yml up -d

# Проверка
$COMPOSE -f docker-compose.prod.yml ps
curl http://localhost:8000/health
```

## Шаг 7: Проверка

```bash
# На сервере
curl http://localhost:8000/health
curl https://onlyface.art/health

# С вашего компьютера
curl https://onlyface.art/health
```

## Шаг 8: Настройка BotFather

1. Откройте @BotFather в Telegram
2. `/mybots` → выберите бота
3. Bot Settings → Menu Button
4. URL: `https://onlyface.art`

## Проблемы и решения

### API не отвечает

```bash
cd ~/facy-app
docker-compose -f docker-compose.prod.yml logs api
docker-compose -f docker-compose.prod.yml restart api
```

### Nginx не работает

```bash
sudo nginx -t
sudo systemctl status nginx
sudo systemctl restart nginx
```

### SSL сертификат не получен

```bash
sudo certbot --nginx -d onlyface.art -d www.onlyface.art
```

## Полезные команды

```bash
# Логи
docker-compose -f docker-compose.prod.yml logs -f

# Перезапуск
docker-compose -f docker-compose.prod.yml restart

# Остановка
docker-compose -f docker-compose.prod.yml down

# Обновление
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

## Структура проекта

- `api/` - FastAPI приложение
- `bot/` - Telegram бот
- `templates/` - HTML шаблоны
- `static/` - Статические файлы
- `docker-compose.prod.yml` - Конфигурация Docker

## Дополнительная информация

- API эндпоинты: см. `API_ENDPOINTS.md`
- Настройка DNS: см. `DNS_SETUP_INSTRUCTIONS.md`
- Настройка SSL: см. `SSL_SETUP.md`

