# Альтернативы Vercel для деплоя

## Проблема с Vercel

Если Vercel не обновляется автоматически:
1. Проверьте, что репозиторий подключен к Vercel
2. Убедитесь, что деплой настроен на ветку `main`
3. Проверьте логи деплоя в Vercel Dashboard
4. Возможно, нужно переподключить репозиторий

## Альтернативные платформы

### 1. Railway (рекомендуется)

**Преимущества:**
- Бесплатный план: $5 кредитов/месяц
- Автоматический HTTPS
- Простая настройка
- Поддержка PostgreSQL
- Автоматический деплой из GitHub

**Настройка:**
1. Зарегистрируйтесь на https://railway.app
2. Подключите GitHub репозиторий
3. Railway автоматически обнаружит `railway.json`
4. Добавьте переменные окружения в настройках проекта
5. Деплой произойдет автоматически

**Переменные окружения:**
- `BOT_TOKEN` - токен Telegram бота
- `DATABASE_URL` - создайте PostgreSQL в Railway (автоматически)
- `WEBAPP_URL` - URL вашего Railway приложения
- `REPLICATE_API_KEY` - ключ Replicate API

---

### 2. Render

**Преимущества:**
- Бесплатный план (с ограничениями)
- Автоматический HTTPS
- Простая настройка
- Поддержка PostgreSQL

**Настройка:**
1. Зарегистрируйтесь на https://render.com
2. Подключите GitHub репозиторий
3. Выберите "New Web Service"
4. Render автоматически обнаружит `render.yaml`
5. Добавьте переменные окружения

**Переменные окружения:**
- `BOT_TOKEN`
- `DATABASE_URL` - создайте PostgreSQL в Render
- `WEBAPP_URL` - URL вашего Render приложения
- `REPLICATE_API_KEY`

---

### 3. Fly.io

**Преимущества:**
- Бесплатный план: 3 shared-cpu-1x VMs
- Глобальная сеть
- Автоматический HTTPS
- Docker-based

**Настройка:**
1. Установите flyctl: `curl -L https://fly.io/install.sh | sh`
2. Зарегистрируйтесь: `fly auth signup`
3. Создайте приложение: `fly launch`
4. Добавьте переменные: `fly secrets set BOT_TOKEN=...`

---

### 4. Netlify

**Преимущества:**
- Бесплатный план
- Отличная поддержка статики
- Serverless функции
- Автоматический HTTPS

**Настройка:**
1. Зарегистрируйтесь на https://netlify.com
2. Подключите GitHub репозиторий
3. Настройте build settings:
   - Build command: `echo "No build needed"`
   - Publish directory: `.`
4. Добавьте переменные окружения

---

### 5. Cloudflare Pages + Workers

**Преимущества:**
- Бесплатный план
- Быстрая CDN
- Serverless функции
- Автоматический HTTPS

**Настройка:**
1. Зарегистрируйтесь на https://pages.cloudflare.com
2. Подключите GitHub репозиторий
3. Настройте Workers для API

---

### 6. DigitalOcean App Platform

**Преимущества:**
- От $5/месяц
- Простая настройка
- Автоматический HTTPS
- Поддержка PostgreSQL

**Настройка:**
1. Зарегистрируйтесь на https://digitalocean.com
2. Создайте App Platform приложение
3. Подключите GitHub репозиторий
4. Добавьте переменные окружения

---

### 7. Heroku

**Преимущества:**
- Простая настройка
- Много дополнений
- Автоматический HTTPS

**Недостатки:**
- Платный (от $7/месяц)
- Нет бесплатного плана

**Настройка:**
1. Установите Heroku CLI
2. `heroku login`
3. `heroku create your-app-name`
4. `git push heroku main`
5. `heroku config:set BOT_TOKEN=...`

---

### 8. VPS с Docker (Yandex Cloud, Timeweb, Selectel)

**Преимущества:**
- Полный контроль
- Нет ограничений
- Можно использовать свой домен

**Настройка:**
1. Создайте VPS
2. Установите Docker: `curl -fsSL https://get.docker.com | sh`
3. Клонируйте репозиторий
4. Запустите: `docker-compose -f docker-compose.prod.yml up -d`

---

## Рекомендации

**Для быстрого старта:**
- Railway (если нужен бесплатный план)
- Render (если Railway недоступен)

**Для продакшена:**
- VPS с Docker (полный контроль)
- DigitalOcean App Platform (простота + надежность)

**Для статики + API:**
- Netlify (отличная поддержка статики)
- Cloudflare Pages (быстрая CDN)

---

## Быстрый деплой на Railway

```bash
# 1. Зарегистрируйтесь на railway.app
# 2. Подключите GitHub репозиторий
# 3. Railway автоматически обнаружит railway.json
# 4. Добавьте переменные окружения в настройках проекта
```

## Быстрый деплой на Render

```bash
# 1. Зарегистрируйтесь на render.com
# 2. Подключите GitHub репозиторий
# 3. Выберите "New Web Service"
# 4. Render автоматически обнаружит render.yaml
# 5. Добавьте переменные окружения
```

## Переменные окружения (для всех платформ)

```env
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname
WEBAPP_URL=https://your-app-url.com
REPLICATE_API_KEY=your_replicate_key
REPLICATE_IMAGE_MODEL=ideogram-ai/ideogram-v3-turbo
REPLICATE_VIDEO_MODEL=minimax/video-01
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
```

