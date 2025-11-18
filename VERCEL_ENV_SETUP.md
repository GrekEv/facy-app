# Настройка переменных окружения в Vercel

## Добавление переменных через Vercel Dashboard

1. Откройте https://vercel.com/dashboard
2. Выберите проект
3. Settings → Environment Variables
4. Add New → Key: `OPENAI_API_KEY`, Value: ваш ключ
5. Выберите окружения (Production, Preview, Development)
6. Save
7. Redeploy последний деплой

## Добавление через Vercel CLI

```bash
npm i -g vercel
vercel login
vercel env add OPENAI_API_KEY
```

## Необходимые переменные

```
BOT_TOKEN=ваш_токен_бота
WEBAPP_URL=https://facy-app.vercel.app
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
OPENAI_API_KEY=sk-ваш_ключ_openai
IMAGE_GENERATION_PROVIDER=openai
```

## Альтернативные провайдеры

```
FFANS_API_KEY=ваш_ключ_ffans
IMAGE_GENERATION_PROVIDER=ffans

REPLICATE_API_KEY=ваш_ключ_replicate
IMAGE_GENERATION_PROVIDER=replicate
```

## Получение OpenAI API ключа

1. https://platform.openai.com/api-keys
2. Create new secret key
3. Скопируйте ключ (начинается с `sk-`)

## Проверка

После добавления переменных сделайте redeploy и проверьте логи:
- Deployments → Functions → api/index → Logs
- Должно быть: `has_openai_key: True`

## Устранение проблем

- Проверьте имя переменной: `OPENAI_API_KEY` (регистр важен)
- Проверьте окружения: Production, Preview
- Сделайте redeploy после добавления переменных

