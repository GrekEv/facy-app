# ⚡ Быстрый деплой Facy

## 🚀 За 5 минут в продакшен

### Шаг 1: GitHub (2 минуты)

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/ваш-username/facy-app.git
git push -u origin main
```

### Шаг 2: Railway (2 минуты)

1. Откройте [railway.app](https://railway.app)
2. Войдите через GitHub
3. **New Project** → **Deploy from GitHub repo**
4. Выберите ваш репозиторий
5. В **Variables** добавьте:

```env
BOT_TOKEN=ваш_токен_от_BotFather
WEBAPP_URL=https://ваш-vercel-url.vercel.app
ENVIRONMENT=production
```

6. Скопируйте Railway URL (например: `https://facy-app.up.railway.app`)

### Шаг 3: Vercel (1 минута)

1. Откройте [vercel.com](https://vercel.com)
2. Войдите через GitHub
3. **Add New Project** → выберите репозиторий
4. В `vercel.json` замените `YOUR-RAILWAY-URL` на ваш Railway URL
5. **Deploy**
6. Скопируйте Vercel URL (например: `https://facy-app.vercel.app`)

### Шаг 4: Обновите переменные

В Railway обновите:
```env
WEBAPP_URL=https://ваш-vercel-url.vercel.app
```

### Шаг 5: Настройте бота

1. Откройте [@BotFather](https://t.me/BotFather)
2. `/mybots` → выберите бота → **Menu Button**
3. URL: `https://ваш-vercel-url.vercel.app`

## ✅ Готово!

Откройте бота в Telegram и нажмите "🚀 Открыть приложение"

---

📖 **Подробная инструкция:** [DEPLOY.md](DEPLOY.md)

