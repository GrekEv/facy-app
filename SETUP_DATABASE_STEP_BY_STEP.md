# Пошаговая настройка базы данных на Timeweb

## Шаг 1: Установка сертификата

### Если сертификат ca.crt в папке проекта:

```bash
# На вашем компьютере (в папке проекта)
cd /Users/kirilldeniushkin/telegram-deepface-app

# Запустите скрипт установки
./install_cert_from_project.sh
```

### Если сертификат в другом месте:

```bash
# Найдите файл
find ~ -name "ca.crt" 2>/dev/null

# Скопируйте в папку проекта
cp /путь/к/ca.crt /Users/kirilldeniushkin/telegram-deepface-app/

# Затем запустите скрипт
cd /Users/kirilldeniushkin/telegram-deepface-app
./install_cert_from_project.sh
```

### Или загрузите вручную:

```bash
# На вашем компьютере (где лежит ca.crt)
scp ca.crt root@72.56.85.215:~/.cloud-certs/root.crt

# Затем на сервере
ssh root@72.56.85.215
chmod 0600 ~/.cloud-certs/root.crt
```

## Шаг 2: Получите данные подключения из Timeweb

1. Откройте https://timeweb.cloud/my/database/4109791/connect
2. В разделе "Подключение" → "Командная строка"
3. Скопируйте данные из команды `psql`:
   - Хост: `ad9d6b1abc9d6aa538e0dea5.twc1.net`
   - Порт: `5432`
   - Пользователь: `gen_user`
   - База: `default_db`
   - Пароль: нажмите на иконку глаза 👁️

## Шаг 3: Обновите DATABASE_URL на сервере

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

**Добавьте новую (замените пароль на ваш):**
```
DATABASE_URL=postgresql+asyncpg://gen_user:ваш_пароль@ad9d6b1abc9d6aa538e0dea5.twc1.net:5432/default_db?ssl=require
```

**Сохраните:** `Ctrl+O`, `Enter`, `Ctrl+X`

## Шаг 4: Перезапустите контейнеры

```bash
# На сервере
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
else
    COMPOSE="docker compose"
fi

$COMPOSE -f docker-compose.prod.yml down
$COMPOSE -f docker-compose.prod.yml up -d

# Подождите 30 секунд
sleep 30

# Проверка
curl http://localhost:8000/api/health
```

## Шаг 5: Проверка

```bash
# На сервере
curl http://localhost:8000/api/health

# С вашего компьютера
curl https://onlyface.art/api/health
```

Должен вернуть JSON с информацией о базе данных.

