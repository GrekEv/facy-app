# Настройка Vercel - Полная инструкция

## Проблема: API не работает на Vercel

Если API не работает, скорее всего проблема в отсутствии `DATABASE_URL`. Без базы данных любой endpoint, который обращается к БД, будет падать с ошибкой 500 или 503.

## Шаг 1: Настройка PostgreSQL базы данных

### Вариант 1: Vercel Postgres (рекомендуется)

1. В проекте Vercel перейдите в **Storage** → **Create Database** → **Postgres**
2. Выберите план (Hobby - бесплатный)
3. Vercel автоматически создаст переменную `POSTGRES_URL`

### Вариант 2: Neon (бесплатный)

1. Зарегистрируйтесь на https://neon.tech
2. Создайте проект и базу данных
3. Скопируйте connection string
4. Преобразуйте в формат для asyncpg:
   ```
   postgresql+asyncpg://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```

### Вариант 3: Railway / Render / Supabase

Любой PostgreSQL провайдер подойдет. Главное - получить connection string в формате:
```
postgresql+asyncpg://user:password@host:port/dbname
```

## Шаг 2: Настройка переменных окружения в Vercel

Перейдите в **Project Settings** → **Environment Variables** и добавьте:

### Обязательные переменные:

```env
# База данных
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
# Или для Vercel Postgres:
DATABASE_URL=$POSTGRES_URL

# Telegram Bot
BOT_TOKEN=your_telegram_bot_token

# Web App URL (ваш домен Vercel или кастомный)
WEBAPP_URL=https://your-app.vercel.app
# Или кастомный домен:
WEBAPP_URL=https://onlyface.art

# Администраторы (опционально)
ADMIN_IDS=123456789,987654321
```

### Для генерации изображений и видео:

```env
# Replicate API
REPLICATE_API_KEY=your_replicate_api_key
REPLICATE_IMAGE_MODEL=ideogram-ai/ideogram-v3-turbo
REPLICATE_VIDEO_MODEL=minimax/video-01

# Email для отправки кодов подтверждения
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=OnlyFace
```

### Опциональные переменные:

```env
# Если используете отдельный backend API
API_BASE_URL=https://your-backend-api.com

# Прокси для внешних API (если нужен)
PROXY_URL=http://proxy-server:port
```

## Шаг 3: Проверка работы

### 1. Проверьте health endpoint:

Откройте в браузере:
```
https://your-app.vercel.app/api/health
```

Должен вернуться JSON:
```json
{
  "status": "ok",
  "database": "connected",
  "api": "ok"
}
```

Если `database: "not_configured"` или `database: "error"` - проверьте `DATABASE_URL`.

### 2. Проверьте реферальную ссылку:

1. Откройте Web App
2. Нажмите "Скопировать ссылку приглашения"
3. Проверьте, что ссылка ведет на правильный домен (из `WEBAPP_URL`)

### 3. Проверьте QR-код:

Откройте в браузере:
```
https://your-app.vercel.app/api/referral/qr?telegram_id=123456789
```

Должен вернуться PNG изображение. Отсканируйте QR - ссылка должна вести на `WEBAPP_URL?ref=...`

## Шаг 4: Деплой

После настройки всех переменных:

1. Перейдите в **Deployments**
2. Нажмите **Redeploy** на последнем деплое
3. Или сделайте новый commit в git - Vercel автоматически задеплоит

## Решение проблем

### Проблема: `database: "not_configured"`

**Причина:** `DATABASE_URL` не установлен или пустой.

**Решение:**
1. Проверьте, что переменная добавлена в Vercel
2. Убедитесь, что формат правильный: `postgresql+asyncpg://...`
3. Для Vercel Postgres используйте: `DATABASE_URL=$POSTGRES_URL`

### Проблема: `database: "error"`

**Причина:** Неправильный connection string или база недоступна.

**Решение:**
1. Проверьте connection string на правильность
2. Убедитесь, что база данных запущена
3. Проверьте, что IP не заблокирован (для некоторых провайдеров)

### Проблема: Реферальная ссылка ведет не туда

**Причина:** `WEBAPP_URL` не установлен или неправильный.

**Решение:**
1. Установите `WEBAPP_URL` в переменные окружения Vercel
2. Убедитесь, что это полный URL с `https://`
3. Перезадеплойте приложение

### Проблема: QR-код ведет не туда

**Причина:** `WEBAPP_URL` не установлен на бэкенде.

**Решение:**
1. Установите `WEBAPP_URL` в переменные окружения Vercel
2. QR-код генерируется на бэкенде, поэтому нужен `WEBAPP_URL` там
3. Перезадеплойте приложение

## Форматы connection string

### Neon:
```
postgresql+asyncpg://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
```

### Railway:
```
postgresql+asyncpg://user:password@host:port/dbname
```

### Vercel Postgres:
```
DATABASE_URL=$POSTGRES_URL
```
(Vercel автоматически подставит значение)

### Supabase:
```
postgresql+asyncpg://user:password@host:port/dbname
```

## Важно

- **Не используйте SQLite на Vercel** - он не работает в serverless окружении
- **Всегда используйте PostgreSQL** для production
- **Проверяйте `/api/health`** после каждого деплоя
- **WEBAPP_URL должен быть полным URL** с `https://`

## Готово!

После настройки всех переменных и деплоя:
- ✅ API будет работать
- ✅ Реферальные ссылки будут правильными
- ✅ QR-коды будут вести на нужный домен
- ✅ База данных будет подключена

