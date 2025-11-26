# Проверка и запуск API на сервере

## Быстрая диагностика

```bash
ssh root@72.56.85.215
cd ~/facy-app
./fix_api_server.sh
```

## Ручная проверка

### 1. Проверка контейнеров

```bash
cd ~/facy-app
docker compose -f docker-compose.prod.yml ps
```

### 2. Проверка файлов

```bash
ls -la ~/facy-app/run_api.py
ls -la ~/facy-app/.env
ls -la ~/facy-app/docker-compose.prod.yml
```

### 3. Запуск контейнеров

```bash
cd ~/facy-app
docker compose -f docker-compose.prod.yml up -d
```

### 4. Проверка логов

```bash
docker compose -f docker-compose.prod.yml logs api
docker compose -f docker-compose.prod.yml logs bot
```

### 5. Проверка health

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/health
```

## Проблемы и решения

### API не отвечает

1. Проверьте контейнеры:
   ```bash
   docker compose -f docker-compose.prod.yml ps
   ```

2. Проверьте логи:
   ```bash
   docker compose -f docker-compose.prod.yml logs api --tail=50
   ```

3. Перезапустите:
   ```bash
   docker compose -f docker-compose.prod.yml restart api
   ```

### run_api.py не найден

1. Проверьте директорию:
   ```bash
   pwd
   ls -la
   ```

2. Найдите правильную директорию:
   ```bash
   find ~ -name "run_api.py" 2>/dev/null
   ```

3. Перейдите в правильную директорию и запустите скрипт

### Порт 8000 занят

1. Проверьте, что занимает порт:
   ```bash
   lsof -i :8000
   ```

2. Остановите старый процесс или измените порт в docker-compose.prod.yml

### База данных не подключена

1. Проверьте .env файл:
   ```bash
   cat ~/facy-app/.env | grep DATABASE_URL
   ```

2. Проверьте подключение:
   ```bash
   curl http://localhost:8000/api/health
   ```

