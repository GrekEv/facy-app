# Чеклист переменных окружения для Vercel

## ✅ У вас уже есть (проверено):

- ✅ BOT_TOKEN
- ✅ WEBAPP_URL  
- ✅ REPLICATE_API_KEY
- ✅ REPLICATE_IMAGE_MODEL
- ✅ REPLICATE_VIDEO_MODEL
- ✅ IMAGE_GENERATION_PROVIDER
- ✅ VIDEO_GENERATION_PROVIDER
- ✅ DATABASE_URL (в .env, нужно проверить формат)

## 📋 Что нужно сделать на Vercel:

### Шаг 1: Откройте Vercel Dashboard

1. Перейдите в ваш проект
2. Откройте **Settings** → **Environment Variables**

### Шаг 2: Добавьте все переменные из .env

Скопируйте все переменные из вашего `.env` файла в Vercel:

```env
BOT_TOKEN=ваш_токен
WEBAPP_URL=https://your-app.vercel.app
REPLICATE_API_KEY=ваш_ключ
REPLICATE_IMAGE_MODEL=ideogram-ai/ideogram-v3-turbo
REPLICATE_VIDEO_MODEL=minimax/video-01
IMAGE_GENERATION_PROVIDER=replicate
VIDEO_GENERATION_PROVIDER=replicate
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
```

### Шаг 3: Настройте DATABASE_URL

**Важно:** Если ваш `DATABASE_URL` начинается с `postgresql://`, нужно преобразовать в `postgresql+asyncpg://`

#### Если у вас Neon (как у вас):

Текущий формат (из Neon):
```
postgresql://neondb_owner:npg_DB2lLYWyVSv5@ep-sweet-thunder-a45uh81b-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**Правильный формат для Vercel:**
```
postgresql+asyncpg://neondb_owner:npg_DB2lLYWyVSv5@ep-sweet-thunder-a45uh81b-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**Просто добавьте `+asyncpg` после `postgresql`**

**Скопируйте это значение в Vercel:**
```
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_DB2lLYWyVSv5@ep-sweet-thunder-a45uh81b-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

#### Если у вас другой провайдер:

Преобразуйте:
```
postgresql://... → postgresql+asyncpg://...
```

### Шаг 4: Опциональные переменные (если нужны)

```env
# Email для отправки кодов подтверждения
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=OnlyFace

# Администраторы
ADMIN_IDS=123456789,987654321

# Прокси (если нужен)
PROXY_URL=http://proxy-server:port
```

### Шаг 5: Перезадеплойте

1. После добавления всех переменных
2. Перейдите в **Deployments**
3. Нажмите **Redeploy** на последнем деплое
4. Или сделайте новый commit в git

### Шаг 6: Проверка

Откройте в браузере:
```
https://your-app.vercel.app/api/health
```

Должен вернуться:
```json
{
  "status": "ok",
  "database": "connected",
  "api": "ok"
}
```

Если `database: "not_configured"`:
- Проверьте, что `DATABASE_URL` добавлен в Vercel
- Проверьте формат: должен быть `postgresql+asyncpg://...`

Если `database: "error"`:
- Проверьте connection string на правильность
- Убедитесь, что база данных запущена
- Проверьте логи деплоя в Vercel

## Быстрая проверка формата DATABASE_URL

Правильный формат:
```
postgresql+asyncpg://user:password@host:port/dbname
```

Для Neon (с SSL):
```
postgresql+asyncpg://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
```

## Готово!

После настройки всех переменных и деплоя:
- ✅ API будет работать
- ✅ База данных будет подключена
- ✅ Реферальные ссылки будут правильными
- ✅ QR-коды будут работать

