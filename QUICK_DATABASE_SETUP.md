# Быстрая настройка DATABASE_URL для Vercel

## У вас уже есть:
- ✅ BOT_TOKEN
- ✅ WEBAPP_URL
- ✅ REPLICATE_API_KEY
- ❌ DATABASE_URL - нужно настроить

## Вариант 1: Vercel Postgres (самый простой)

1. В проекте Vercel перейдите в **Storage**
2. Нажмите **Create Database** → **Postgres**
3. Выберите план **Hobby** (бесплатный)
4. Vercel автоматически создаст переменную `POSTGRES_URL`

5. В **Settings** → **Environment Variables** добавьте:
   ```
   DATABASE_URL=$POSTGRES_URL
   ```
   
   Или скопируйте значение `POSTGRES_URL` и используйте напрямую.

6. Перезадеплойте проект

**Готово!** База данных настроена.

---

## Вариант 2: Neon (бесплатный, быстрый)

1. Зарегистрируйтесь на https://neon.tech
2. Создайте новый проект
3. Скопируйте **Connection string**
4. Преобразуйте в формат для asyncpg:
   ```
   postgresql+asyncpg://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```
   
   Если connection string уже в формате `postgresql://...`, просто добавьте `+asyncpg`:
   ```
   postgresql://... → postgresql+asyncpg://...
   ```

5. В Vercel → **Settings** → **Environment Variables** добавьте:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```

6. Перезадеплойте проект

---

## Вариант 3: Railway PostgreSQL

1. Зарегистрируйтесь на https://railway.app
2. Создайте новый проект
3. Добавьте **PostgreSQL** сервис
4. В настройках PostgreSQL скопируйте **Connection URL**
5. Преобразуйте в формат:
   ```
   postgresql+asyncpg://user:password@host:port/dbname
   ```

6. В Vercel → **Settings** → **Environment Variables** добавьте:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
   ```

7. Перезадеплойте проект

---

## Вариант 4: Supabase (бесплатный)

1. Зарегистрируйтесь на https://supabase.com
2. Создайте новый проект
3. Перейдите в **Settings** → **Database**
4. Скопируйте **Connection string** (URI)
5. Преобразуйте в формат:
   ```
   postgresql+asyncpg://user:password@host:port/dbname
   ```

6. В Vercel → **Settings** → **Environment Variables** добавьте:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
   ```

7. Перезадеплойте проект

---

## Проверка работы

После настройки `DATABASE_URL` и деплоя:

1. Откройте в браузере:
   ```
   https://your-app.vercel.app/api/health
   ```

2. Должен вернуться JSON:
   ```json
   {
     "status": "ok",
     "database": "connected",
     "api": "ok"
   }
   ```

3. Если `database: "not_configured"` или `database: "error"`:
   - Проверьте формат `DATABASE_URL`
   - Убедитесь, что база данных запущена
   - Проверьте логи деплоя в Vercel

---

## Форматы connection string

### Правильный формат для asyncpg:
```
postgresql+asyncpg://user:password@host:port/dbname
```

### Для Neon (с SSL):
```
postgresql+asyncpg://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
```

### Для Vercel Postgres:
```
DATABASE_URL=$POSTGRES_URL
```
(Или скопируйте значение `POSTGRES_URL`)

---

## Важно

- **НЕ используйте SQLite** на Vercel - он не работает в serverless
- **Всегда используйте PostgreSQL** для production
- Формат должен быть `postgresql+asyncpg://...` (не просто `postgresql://...`)
- Для Neon обязательно добавьте `?sslmode=require` в конец URL

---

## Рекомендация

**Используйте Vercel Postgres** - это самый простой вариант:
- Автоматическая настройка
- Бесплатный план Hobby
- Автоматическое создание переменной `POSTGRES_URL`
- Не нужно настраивать SSL вручную

