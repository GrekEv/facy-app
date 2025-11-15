# 🤖 Автоматический деплой Facy

Этот документ описывает как настроить полностью автоматический деплой при каждом пуше в `main`.

## 🚀 Быстрый старт

### Вариант 1: Через скрипт (рекомендуется)

```bash
chmod +x setup-deploy.sh
./setup-deploy.sh
```

Скрипт проведет вас через все шаги настройки.

### Вариант 2: Вручную

## 📋 Шаг 1: Установка инструментов

### GitHub CLI
```bash
brew install gh
gh auth login
```

### Railway CLI
```bash
npm i -g @railway/cli
railway login
```

### Vercel CLI
```bash
npm i -g vercel
vercel login
```

## 🔧 Шаг 2: Настройка Railway

1. **Создайте проект:**
```bash
railway init
```

2. **Подключите репозиторий:**
   - В Railway Dashboard: Settings → Connect GitHub Repo
   - Выберите `GrekEv/facy-app`

3. **Настройте переменные:**
```bash
railway variables set BOT_TOKEN="ваш_токен_от_BotFather"
railway variables set WEBAPP_URL="https://ваш-vercel-url.vercel.app"
railway variables set ENVIRONMENT="production"
```

4. **Получите Railway URL:**
   - В Railway Dashboard скопируйте URL (например: `https://facy-app.up.railway.app`)

## ▲ Шаг 3: Настройка Vercel

1. **Создайте проект:**
```bash
vercel
```

2. **Обновите vercel.json:**
   - Замените `YOUR-RAILWAY-URL` на ваш Railway URL
   - Или используйте скрипт: `./setup-deploy.sh` → вариант 4

3. **Деплой:**
```bash
vercel --prod
```

4. **Получите Vercel URL:**
   - Скопируйте URL из вывода команды (например: `https://facy-app.vercel.app`)

## 🔄 Шаг 4: Обновите Railway

Обновите `WEBAPP_URL` в Railway на ваш Vercel URL:
```bash
railway variables set WEBAPP_URL="https://ваш-vercel-url.vercel.app"
```

## 🔐 Шаг 5: Настройка GitHub Secrets

Для автоматического деплоя через GitHub Actions:

1. **Получите Railway Token:**
   - https://railway.app/account → Tokens → New Token
   - Скопируйте токен

2. **Получите Vercel Token:**
   - https://vercel.com/account/tokens → Create Token
   - Скопируйте токен

3. **Получите Vercel Project ID:**
   - В Vercel Dashboard → Project Settings → General
   - Скопируйте Project ID

4. **Получите Vercel Org ID:**
   - В Vercel Dashboard → Team Settings → General
   - Скопируйте Team ID (это и есть Org ID)

5. **Добавьте секреты в GitHub:**
```bash
gh secret set RAILWAY_TOKEN --body "ваш_railway_токен"
gh secret set VERCEL_TOKEN --body "ваш_vercel_токен"
gh secret set VERCEL_ORG_ID --body "ваш_org_id"
gh secret set VERCEL_PROJECT_ID --body "ваш_project_id"
```

Или через веб-интерфейс:
- GitHub → Settings → Secrets and variables → Actions → New repository secret

## ✅ Шаг 6: Проверка

После настройки:

1. **Сделайте тестовый коммит:**
```bash
git add .
git commit -m "Test deploy"
git push
```

2. **Проверьте деплой:**
   - Railway: https://railway.app → ваш проект → Deployments
   - Vercel: https://vercel.com → ваш проект → Deployments
   - GitHub Actions: https://github.com/GrekEv/facy-app/actions

## 🔄 Автоматический деплой

После настройки, каждый push в `main` автоматически:
- Задеплоит на Railway
- Задеплоит на Vercel

Проверьте `.github/workflows/deploy.yml` для деталей.

## 🐛 Решение проблем

### Railway не деплоит
- Проверьте Railway Token в GitHub Secrets
- Убедитесь, что проект подключен к GitHub репозиторию

### Vercel не деплоит
- Проверьте Vercel Token, Org ID и Project ID в GitHub Secrets
- Убедитесь, что проект создан через `vercel` команду

### GitHub Actions не запускается
- Проверьте что файл `.github/workflows/deploy.yml` существует
- Проверьте что все секреты добавлены
- Проверьте логи в GitHub Actions

## 📝 Ручной деплой

Если автоматический деплой не работает, можно деплоить вручную:

### Railway
```bash
railway up
```

### Vercel
```bash
vercel --prod
```

## 🔗 Полезные ссылки

- [Railway Docs](https://docs.railway.app)
- [Vercel Docs](https://vercel.com/docs)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

