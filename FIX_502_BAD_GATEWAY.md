# Исправление 502 Bad Gateway

## Проблема
Nginx работает, но не может подключиться к API на `localhost:8000`.

## Причина
API (FastAPI) не запущен или не отвечает на порту 8000.

## Решение

### 1. Подключитесь к серверу

```bash
ssh root@72.56.85.215
cd ~/facy-app
```

### 2. Проверьте, запущен ли API

```bash
# Проверка API локально
curl http://localhost:8000/health

# Если не отвечает - API не запущен
```

### 3. Запустите API (Docker Compose)

```bash
# Определите команду docker compose
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
else
    COMPOSE="docker compose"
fi

# Проверка статуса контейнеров
$COMPOSE -f docker-compose.prod.yml ps

# Запуск контейнеров
$COMPOSE -f docker-compose.prod.yml up -d

# Проверка логов
$COMPOSE -f docker-compose.prod.yml logs api

# Проверка, что API отвечает
curl http://localhost:8000/health
```

### 4. Если контейнеры не запускаются

```bash
# Проверка .env файла
cat .env | grep -E "BOT_TOKEN|WEBAPP_URL|DATABASE_URL"

# Пересборка контейнеров
$COMPOSE -f docker-compose.prod.yml down
$COMPOSE -f docker-compose.prod.yml up -d --build

# Проверка логов на ошибки
$COMPOSE -f docker-compose.prod.yml logs --tail=50
```

### 5. Проверка порта 8000

```bash
# Проверка, что порт 8000 слушается
netstat -tlnp | grep 8000
# или
ss -tlnp | grep 8000

# Проверка, что процесс слушает порт
lsof -i :8000
```

### 6. Если API запущен, но Nginx не может подключиться

```bash
# Проверка конфигурации Nginx
sudo nginx -t

# Проверка, что Nginx проксирует на правильный адрес
sudo cat /etc/nginx/sites-enabled/onlyface | grep proxy_pass

# Должно быть: proxy_pass http://localhost:8000;

# Перезапуск Nginx
sudo systemctl restart nginx
```

## Быстрое решение (если есть скрипт)

```bash
ssh root@72.56.85.215
cd ~/facy-app

# Запуск API
./start_api_on_server.sh

# Или полная настройка
./setup_domain_onlyface.sh
```

## Проверка после исправления

```bash
# На сервере
curl http://localhost:8000/health

# С вашего компьютера
curl https://onlyface.art/health
```

## Типичные проблемы

### Проблема: Контейнеры не запускаются
**Решение:**
```bash
# Проверьте логи
docker compose -f docker-compose.prod.yml logs

# Проверьте .env файл
cat .env

# Убедитесь, что BOT_TOKEN установлен
```

### Проблема: Порт 8000 занят другим процессом
**Решение:**
```bash
# Найдите процесс
lsof -i :8000

# Остановите старый процесс или измените порт в docker-compose.prod.yml
```

### Проблема: База данных не подключена
**Решение:**
```bash
# Проверьте DATABASE_URL в .env
cat .env | grep DATABASE_URL

# Если SQLite, убедитесь что файл существует
ls -la data/app.db
```

## Важно

- **502 Bad Gateway** = Nginx работает, но API не отвечает
- **ERR_CONNECTION_REFUSED** = Nginx не запущен
- Всегда проверяйте `curl http://localhost:8000/health` на сервере перед проверкой через домен

