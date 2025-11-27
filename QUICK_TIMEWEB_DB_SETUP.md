# Быстрая настройка PostgreSQL на Timeweb

## Шаг 1: Получите данные подключения

1. Откройте базу данных в панели Timeweb
2. Вкладка **"Подключение"** → **"Командная строка"**
3. Выберите:
   - Пользователь: `gen_user` (или другой)
   - База данных: `default_db` (или другая)
4. Скопируйте данные из команды `psql`:
   - Хост: `ad9d6b1abc9d6aa538e0dea5.twc1.net` (формат `xxxxx.twc1.net`)
   - Порт: `5432`
   - Пользователь: `gen_user`
   - База: `default_db`
   - Пароль: нажмите на иконку глаза, чтобы увидеть

## Шаг 2: Обновите .env на сервере

```bash
ssh root@72.56.85.215
cd ~/facy-app

# Откройте .env
nano .env
```

**Удалите старую строку:**
```
DATABASE_URL=postgresql+asyncpg://facy_user:etxX4gk272PdJYH@rc1a-6t9pb3se81b4idf5.mdb.yandexcloud.net:6432/facy_db?ssl=require
```

**Добавьте новую (замените на ваши данные):**
```
DATABASE_URL=postgresql+asyncpg://gen_user:ваш_пароль@ad9d6b1abc9d6aa538e0dea5.twc1.net:5432/default_db?ssl=require
```

**Пример с реальными данными:**
```
DATABASE_URL=postgresql+asyncpg://gen_user:e%7D%2B%400Go~xgGcwt@ad9d6b1abc9d6aa538e0dea5.twc1.net:5432/default_db?ssl=require
```

**Важно:**
- Формат хоста: `xxxxx.twc1.net` (не `postgres-xxx.timeweb.cloud`)
- Формат: `postgresql+asyncpg://` (не просто `postgresql://`)
- Параметр `?ssl=require` обязателен
- Если пароль содержит `@`, `+`, `~` и т.д., можно использовать как есть или URL-кодировать

**Сохраните:** `Ctrl+O`, `Enter`, `Ctrl+X`

## Шаг 3: Перезапустите контейнеры

```bash
# Определите команду
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
else
    COMPOSE="docker compose"
fi

# Перезапуск
$COMPOSE -f docker-compose.prod.yml down
$COMPOSE -f docker-compose.prod.yml up -d

# Подождите 30 секунд
sleep 30

# Проверка
curl http://localhost:8000/api/health
```

## Шаг 4: Проверка

```bash
# Должен вернуть JSON с информацией о БД
curl http://localhost:8000/api/health

# Проверка логов
$COMPOSE -f docker-compose.prod.yml logs api | grep -i database
```

## Если не работает

1. **Проверьте формат хоста:** должен быть `xxxxx.twc1.net`
2. **Проверьте пароль:** скопируйте точно из панели Timeweb
3. **Проверьте формат:** `postgresql+asyncpg://` (не `postgresql://`)
4. **Проверьте SSL:** должен быть `?ssl=require` в конце
5. **Посмотрите логи:** `docker compose -f docker-compose.prod.yml logs api`

## Альтернатива: SQLite

Если не хотите настраивать PostgreSQL:

```bash
ssh root@72.56.85.215
cd ~/facy-app

# Удалите DATABASE_URL
sed -i '/^DATABASE_URL=/d' .env

# Перезапустите
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

SQLite создастся автоматически в `data/app.db`.

