# Проверка на сервере (не на локальном компьютере!)

## Важно!
Все команды проверки выполняются **на сервере через SSH**, а не на вашем локальном компьютере!

## Правильная последовательность:

### 1. Подключитесь к серверу

```bash
ssh root@72.56.85.215
```

### 2. Перейдите в директорию проекта

```bash
cd ~/facy-app
```

### 3. Проверьте DATABASE_URL

```bash
# Проверьте что записалось (пароль будет скрыт)
grep DATABASE_URL .env | sed 's/:[^:@]*@/:***@/'
```

Должно быть:
```
DATABASE_URL=postgresql+asyncpg://gen_user:***@ad9d6b1abc9d6aa538e0dea5.twc1.net:5432/default_db?ssl=require
```

### 4. Перезапустите контейнеры (НА СЕРВЕРЕ!)

```bash
# Определите команду
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
else
    COMPOSE="docker compose"
fi

# Остановите
$COMPOSE -f docker-compose.prod.yml down

# Запустите
$COMPOSE -f docker-compose.prod.yml up -d

# Подождите 30 секунд
sleep 30
```

### 5. Проверьте статус контейнеров (НА СЕРВЕРЕ!)

```bash
# Статус
$COMPOSE -f docker-compose.prod.yml ps

# Должны быть в статусе "Up" или "Running"
```

### 6. Проверьте health endpoint (НА СЕРВЕРЕ!)

```bash
# На сервере
curl http://localhost:8000/health

# Или
curl http://localhost:8000/api/health
```

Должен вернуть JSON, а не ошибку подключения.

### 7. Проверьте логи (НА СЕРВЕРЕ!)

```bash
# Логи API
$COMPOSE -f docker-compose.prod.yml logs api --tail=50

# Ищите ошибки подключения к БД
$COMPOSE -f docker-compose.prod.yml logs api | grep -i database
```

### 8. Проверка через домен (с вашего компьютера)

Только после того, как на сервере всё работает:

```bash
# С вашего локального компьютера
curl https://onlyface.art/health
curl https://onlyface.art/api/health
```

## Если на сервере curl localhost:8000 не работает:

1. **Проверьте, запущены ли контейнеры:**
   ```bash
   docker compose -f docker-compose.prod.yml ps
   ```

2. **Проверьте логи:**
   ```bash
   docker compose -f docker-compose.prod.yml logs api --tail=50
   ```

3. **Проверьте порт:**
   ```bash
   netstat -tlnp | grep 8000
   # или
   ss -tlnp | grep 8000
   ```

4. **Перезапустите контейнеры:**
   ```bash
   docker compose -f docker-compose.prod.yml restart api
   ```

## Итого:

- ✅ Все проверки делаются **на сервере через SSH**
- ✅ `curl http://localhost:8000/health` выполняется **на сервере**
- ✅ Только финальная проверка `curl https://onlyface.art/health` делается с вашего компьютера

