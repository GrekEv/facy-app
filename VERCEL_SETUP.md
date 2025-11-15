# ▲ Настройка Vercel - ИНСТРУКЦИЯ

## Быстрая настройка

1. **Откройте Vercel:**
   - https://vercel.com
   - Войдите через GitHub

2. **Создайте проект:**
   - Нажмите "Add New Project"
   - Найдите и выберите `GrekEv/facy-app`
   - Нажмите "Import"

3. **ВАЖНО: Обновите vercel.json ПЕРЕД деплоем!**

   В GitHub репозитории:
   - Откройте файл `vercel.json`
   - Нажмите "Edit" (карандаш)
   - Найдите все вхождения `YOUR-RAILWAY-URL`
   - Замените на ваш Railway URL (БЕЗ `https://`)
   
   Например, если Railway URL: `https://facy-app.up.railway.app`
   
   Замените на: `facy-app.up.railway.app`
   
   Должно получиться:
   ```json
   {
     "src": "/api/(.*)",
     "dest": "https://facy-app.up.railway.app/api/$1"
   }
   ```
   
   - Нажмите "Commit changes"
   - Vercel автоматически задеплоит после коммита

4. **Или деплой вручную:**
   - После обновления `vercel.json` в GitHub
   - Вернитесь в Vercel
   - Нажмите "Deploy" (или подождите автоматического деплоя)

5. **Получите Vercel URL:**
   - После деплоя скопируйте URL
   - Например: `https://facy-app.vercel.app`

## ✅ Готово!

После получения Vercel URL:
1. Вернитесь в Railway
2. Обновите переменную `WEBAPP_URL` на ваш Vercel URL
3. Настройте Telegram бота (см. BOT_SETUP.md)

---

**Vercel URL:** Скопируйте его для обновления Railway!

