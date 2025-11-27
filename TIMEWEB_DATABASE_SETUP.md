# Настройка базы данных на Timeweb

## Варианты

### 1. SQLite (рекомендуется для начала)

Локальная база данных, не требует настройки. Просто удалите `DATABASE_URL` из `.env` или не указывайте его.

**Преимущества:**
- Не требует настройки
- Работает сразу
- Подходит для небольших проектов

**Недостатки:**
- Медленнее PostgreSQL
- Не подходит для высоких нагрузок

### 2. PostgreSQL на Timeweb

Создайте базу данных через панель Timeweb:

1. Откройте https://timeweb.cloud/
2. Перейдите в раздел **"Базы данных"** или **"Databases"**
3. Нажмите **"Создать базу данных"**
4. Выберите **PostgreSQL**
5. Укажите:
   - Имя базы данных (например: `facy_db`)
   - Пользователь (например: `facy_user`)
   - Пароль (сгенерируйте надежный)
6. После создания скопируйте данные подключения

**Формат DATABASE_URL:**
```
postgresql+asyncpg://пользователь:пароль@хост:порт/база_данных?ssl=require
```

**Пример:**
```
postgresql+asyncpg://facy_user:mypassword@postgres.timeweb.cloud:5432/facy_db?ssl=require
```

### 3. Внешняя PostgreSQL

Если у вас есть внешняя база данных PostgreSQL, используйте её connection string.

## Настройка на сервере

### Автоматически (скрипт)

```bash
ssh root@72.56.85.215
cd ~/facy-app

# Скачайте скрипт
wget https://raw.githubusercontent.com/GrekEv/facy-app/main/setup_timeweb_db.sh
chmod +x setup_timeweb_db.sh
./setup_timeweb_db.sh
```

### Вручную

```bash
ssh root@72.56.85.215
cd ~/facy-app

# Отредактируйте .env
nano .env

# Для SQLite - удалите или закомментируйте DATABASE_URL:
# DATABASE_URL=

# Для PostgreSQL на Timeweb - добавьте:
# DATABASE_URL=postgresql+asyncpg://пользователь:пароль@хост:порт/база?ssl=require

# Перезапустите контейнеры
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

## Удаление старого Yandex Cloud DATABASE_URL

Если в `.env` есть старый DATABASE_URL от Yandex Cloud, удалите его:

```bash
ssh root@72.56.85.215
cd ~/facy-app

# Удалить строку с Yandex Cloud
sed -i '/mdb.yandexcloud.net/d' .env

# Или отредактируйте вручную
nano .env
```

## Проверка

```bash
# На сервере
curl http://localhost:8000/api/health

# Должен вернуть JSON с информацией о базе данных
```

## Важно

- **SQLite** - база данных создается автоматически в `data/app.db`
- **PostgreSQL** - нужно создать базу данных через панель Timeweb
- Формат для asyncpg: `postgresql+asyncpg://...` (не просто `postgresql://`)
- Для Timeweb PostgreSQL обычно требуется `?ssl=require`

