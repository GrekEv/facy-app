# Исправление ошибки 500 на Vercel

## Проблема

При нажатии "Сгенерировать" сервер возвращает **500 ошибку с HTML** вместо JSON.

**Причина:** FastAPI не может стартовать из-за отсутствующих обязательных переменных окружения.

## Что происходит

1. Фронт отправляет `POST /api/generate/image`
2. Сервер отвечает **500 с HTML** (страница ошибки Vercel)
3. Фронт видит `content-type` не `application/json` и показывает системное окно:
   ```
   "ПОДТВЕРДИТЕ ДЕЙСТВИЕ НА ... Ошибка сервера:"
   ```

## Корневая причина

В `config.py` есть обязательные переменные:

```python
class Settings(BaseSettings):
    BOT_TOKEN: str  # ОБЯЗАТЕЛЬНО!
    DATABASE_URL: str  # ОБЯЗАТЕЛЬНО!
    # ...
```

Если `BOT_TOKEN` отсутствует в Environment Variables на Vercel, то при импорте:

```python
settings = Settings()
```

Приложение падает с `ValidationError`, и **FastAPI даже не стартует**.

Vercel в таком случае отдаёт свою HTML-страницу 500, а не наш JSON.

## Решение

### Шаг 1: Проверьте Environment Variables на Vercel

Зайдите в **Vercel → Project → Settings → Environment Variables**.

**Обязательно должны быть:**

```env
BOT_TOKEN=8254778202:AAH-1RebJBOKpr5fKorcIcFHqKAihbCBQ_o
```

```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_DB2lLYWyVSv5@ep-sweet-thunder-a45uh81b-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

```env
WEBAPP_URL=https://facy-mdq1fcr13-kirills-projects-4693373f.vercel.app
```

**Хотя бы один из ключей генерации:**

```env
REPLICATE_API_KEY=your_replicate_api_key
```

Или (если используете FFans):

```env
FFANS_API_KEY=your_key
FFANS_API_URL=your_url
```

### Шаг 2: Сохраните и перезадеплойте

1. Нажмите **Save** в Environment Variables
2. Перейдите в **Deployments**
3. Найдите последний деплой
4. Нажмите **⋮** → **Redeploy**

### Шаг 3: Проверьте, что сервер жив

**Перед тем как снова жать "Сгенерировать":**

Откройте в браузере:
```
https://facy-mdq1fcr13-kirills-projects-4693373f.vercel.app/api/health
```

**Должен прийти JSON:**

```json
{
  "status": "ok",
  "database": "connected",
  "api": "ok"
}
```

**Если видите HTML-страницу Vercel "Internal Server Error":**
- Backend все еще не стартанул
- Проверьте Environment Variables еще раз
- Проверьте логи в Vercel → Deployments → Functions / Logs

### Шаг 4: Проверьте в DevTools

1. Откройте **DevTools → Network**
2. Нажмите **"Сгенерировать"**
3. Найдите запрос `/api/generate/image`
4. Посмотрите **Status** (должен быть 200, не 500)
5. Вкладка **Response** должна показать JSON, а не HTML

**Если там HTML:**
- Проблема на уровне старта приложения
- Отсутствующие env переменные
- Ошибка импорта
- Библиотека не установлена

## Чеклист обязательных переменных

Минимум для работы:

- [ ] `BOT_TOKEN` - токен бота от BotFather
- [ ] `DATABASE_URL` - строка подключения к PostgreSQL в формате `postgresql+asyncpg://...`
- [ ] `WEBAPP_URL` - URL вашего WebApp
- [ ] `REPLICATE_API_KEY` - ключ от Replicate (для генерации изображений/видео)

Дополнительно (если используются):

- [ ] `REPLICATE_IMAGE_MODEL` - модель для генерации изображений
- [ ] `REPLICATE_VIDEO_MODEL` - модель для генерации видео
- [ ] `IMAGE_GENERATION_PROVIDER` - провайдер (replicate/ffans)
- [ ] `VIDEO_GENERATION_PROVIDER` - провайдер (replicate/ffans)
- [ ] `ADMIN_IDS` - ID админов через запятую
- [ ] `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - для email авторизации

## Как проверить логи на Vercel

1. **Vercel Dashboard** → ваш проект
2. **Deployments** → выберите последний деплой
3. **Functions** / **Logs**

Там будет видна точная ошибка, например:
```
ValidationError: BOT_TOKEN is required
```

или

```
ValueError: DATABASE_URL not set
```

## Быстрая проверка

После настройки переменных и перезадеплоя:

1. Откройте `/api/health` → должен быть JSON с `"database": "connected"`
2. Откройте DevTools → Network
3. Нажмите "Сгенерировать"
4. Проверьте, что `/api/generate/image` возвращает JSON, а не HTML

## Резюме

**Окно "ПОДТВЕРДИТЕ ДЕЙСТВИЕ НА ... Ошибка сервера:" говорит только одно:**

Сервер на Vercel отдает 500, а не JSON.

**Нужно:**
1. Добавить все обязательные переменные окружения
2. Убедиться, что `/api/health` возвращает JSON, а не HTML
3. Только после этого пробовать генерацию

