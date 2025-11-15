# ⚡ БЫСТРЫЙ СТАРТ - ВСЕ ТОКЕНЫ ГОТОВЫ

## 🎯 Что у вас есть:

✅ **GitHub репозиторий:** https://github.com/GrekEv/facy-app  
✅ **GitHub токен:** (см. TOKENS.md)  
✅ **Telegram Bot токен:** (см. TOKENS.md)

## 🚀 Деплой за 3 шага:

### Шаг 1: Railway (5 минут)

1. Откройте: https://railway.app → Login with GitHub
2. New Project → Deploy from GitHub repo → `GrekEv/facy-app`
3. Variables → добавьте:
   - `BOT_TOKEN` = `8374729179:AAG7wyo467ksUQgNyoESNzc09Wn0UBS7T7g`
   - `WEBAPP_URL` = `https://ваш-vercel-url.vercel.app` (пока временный)
   - `ENVIRONMENT` = `production`
4. Скопируйте Railway URL (например: `https://facy-app.up.railway.app`)

**📖 Подробнее:** [RAILWAY_SETUP.md](RAILWAY_SETUP.md)

---

### Шаг 2: Vercel (3 минуты)

1. Откройте: https://vercel.com → Login with GitHub
2. Add New Project → `GrekEv/facy-app` → Import
3. **ВАЖНО:** Обновите `vercel.json` в GitHub:
   - Откройте файл `vercel.json` в репозитории
   - Замените `YOUR-RAILWAY-URL` на ваш Railway URL (без `https://`)
   - Commit changes
4. Vercel автоматически задеплоит
5. Скопируйте Vercel URL (например: `https://facy-app.vercel.app`)

**📖 Подробнее:** [VERCEL_SETUP.md](VERCEL_SETUP.md)

---

### Шаг 3: Обновите Railway и настройте бота (2 минуты)

1. **Railway:**
   - Variables → обновите `WEBAPP_URL` на ваш Vercel URL

2. **Telegram Bot:**
   - Откройте: https://t.me/BotFather
   - `/mybots` → выберите бота → Menu Button
   - URL: ваш Vercel URL
   - Save

**📖 Подробнее:** [BOT_SETUP.md](BOT_SETUP.md)

---

## ✅ Готово!

Откройте бота в Telegram → `/start` → "🚀 Открыть приложение"

---

## 🔍 Проверка работы:

- **API:** https://ваш-railway-url.up.railway.app/health → должно быть `{"status": "healthy"}`
- **Web App:** https://ваш-vercel-url.vercel.app → должна открыться главная страница
- **Бот:** Откройте в Telegram → должно открыться приложение

---

## 📚 Дополнительная документация:

- [DEPLOY.md](DEPLOY.md) - Полная инструкция
- [WEB_DEPLOY.md](WEB_DEPLOY.md) - Детальная инструкция через веб-интерфейсы
- [AUTO_DEPLOY.md](AUTO_DEPLOY.md) - Автоматический деплой через CLI

---

**Время деплоя: ~10 минут** ⏱️

