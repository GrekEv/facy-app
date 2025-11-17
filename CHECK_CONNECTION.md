# ✅ Проверка подключения к Yandex Cloud

## 📋 Быстрая проверка подключения

### 1. Проверка базы данных (локально)

```bash
python3 check_connection.py
```

### 2. Проверка на сервере Yandex Cloud

#### Шаг 1: Подключитесь к серверу
```bash
ssh ubuntu@158.160.96.182
```

#### Шаг 2: Проверьте статус контейнеров
```bash
cd ~/facy-app
docker compose -f docker-compose.prod.yml ps
```

#### Шаг 3: Проверьте переменные окружения
```bash
docker compose -f docker-compose.prod.yml exec api env | grep DATABASE_URL
```

Должно быть:
```
DATABASE_URL=postgresql+asyncpg://facy_user:etxX4gk272PdJYH@rc1a-6t9pb3se81b4idf5.mdb.yandexcloud.net:6432/facy_db?ssl=require
```

#### Шаг 4: Проверьте логи приложения
```bash
docker compose -f docker-compose.prod.yml logs api | grep -i "database\|postgres\|connected"
```

Должно быть сообщение: `✓ Database initialized`

#### Шаг 5: Проверьте API
```bash
curl http://localhost:8000/health
```

Должно вернуться: `{"status":"healthy"}`

## 🔧 Если нужно обновить DATABASE_URL на сервере

### Вариант 1: Через SSH (рекомендуется)

```bash
# Подключитесь к серверу
ssh ubuntu@158.160.96.182

# Откройте .env файл
cd ~/facy-app
nano .env

# Найдите строку DATABASE_URL и замените на:
DATABASE_URL=postgresql+asyncpg://facy_user:etxX4gk272PdJYH@rc1a-6t9pb3se81b4idf5.mdb.yandexcloud.net:6432/facy_db?ssl=require

# Сохраните (Ctrl+O, Enter, Ctrl+X)

# Пересоздайте контейнеры
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### Вариант 2: Через команду sed (быстро)

```bash
ssh ubuntu@158.160.96.182 "cd ~/facy-app && sed -i 's|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://facy_user:etxX4gk272PdJYH@rc1a-6t9pb3se81b4idf5.mdb.yandexcloud.net:6432/facy_db?ssl=require|' .env && docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml up -d"
```

## ✅ Текущий статус подключения

### База данных PostgreSQL на Yandex Cloud
- ✅ **Подключена и работает**
- Хост: `rc1a-6t9pb3se81b4idf5.mdb.yandexcloud.net:6432`
- База данных: `facy_db`
- Пользователь: `facy_user`
- Версия PostgreSQL: 15.14

### Сервер Yandex Cloud
- ✅ **Приложение запущено**
- IP: `158.160.96.182`
- API доступен: `http://158.160.96.182:8000`
- Health check: `{"status":"healthy"}`

## 🐛 Решение проблем

### Проблема: Контейнеры не видят новые переменные окружения

**Решение:** Пересоздайте контейнеры (не просто restart):
```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### Проблема: Ошибка подключения к PostgreSQL

**Проверьте:**
1. Правильность DATABASE_URL в `.env`
2. Группы безопасности в Yandex Cloud (порт 6432 должен быть открыт)
3. Доступность хоста PostgreSQL
4. Правильность пароля и имени пользователя

### Проблема: SSH подключение не работает

См. инструкцию: [SSH_TROUBLESHOOT.md](SSH_TROUBLESHOOT.md)

## 📝 Полезные команды

```bash
# Просмотр логов
docker compose -f docker-compose.prod.yml logs -f

# Перезапуск контейнеров
docker compose -f docker-compose.prod.yml restart

# Остановка приложения
docker compose -f docker-compose.prod.yml down

# Запуск приложения
docker compose -f docker-compose.prod.yml up -d

# Проверка статуса
docker compose -f docker-compose.prod.yml ps
```

