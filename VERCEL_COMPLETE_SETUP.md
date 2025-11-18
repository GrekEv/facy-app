# Полная инструкция по настройке Vercel

## 1. Окружение: обязательные переменные на Vercel

### ⚠️ ВАЖНО: Без этих переменных FastAPI не стартует!

Если `BOT_TOKEN` или `DATABASE_URL` отсутствуют, приложение падает с `ValidationError` при импорте `config.py`, и Vercel отдает HTML-страницу 500 вместо JSON.

### Минимум (обязательно):

```env
# ОБЯЗАТЕЛЬНО! Без этого приложение не стартует
BOT_TOKEN=8254778202:AAH-1RebJBOKpr5fKorcIcFHqKAihbCBQ_o

# ОБЯЗАТЕЛЬНО! Без этого приложение не стартует
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_DB2lLYWyVSv5@ep-sweet-thunder-a45uh81b-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require

# ОБЯЗАТЕЛЬНО! Для реферальных ссылок и QR-кодов
WEBAPP_URL=https://your-app.vercel.app
# Или кастомный домен:
# WEBAPP_URL=https://onlyface.app

# ОБЯЗАТЕЛЬНО! Для генерации изображений/видео
REPLICATE_API_KEY=your_replicate_api_key

# Опционально
ADMIN_IDS=123456789,987654321
```

### Дополнительно (если используются):

```env
REPLICATE_IMAGE_MODEL=ideogram-ai/ideogram-v3-turbo
REPLICATE_VIDEO_MODEL=minimax/video-01
IMAGE_GENERATION_PROVIDER=replicate
VIDEO_GENERATION_PROVIDER=replicate

# Email для отправки кодов подтверждения
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=OnlyFace

# Прокси (если нужен)
PROXY_URL=http://proxy-server:port
```

### Что сделать:

1. Откройте `ENV_EXAMPLE.txt` в проекте
2. Все значимые переменные добавьте в **Vercel → Settings → Environment Variables**
3. После сохранения сделайте **Redeploy** проекта

---

## 2. Telegram Mini App и связка с WebApp

### В BotFather:

1. Откройте [@BotFather](https://t.me/BotFather)
2. Отправьте `/mybots`
3. Выберите вашего бота
4. Выберите **Bot Settings** → **Menu Button**
5. Установите URL: `https://your-app.vercel.app` (или ваш кастомный домен)

### В коде бота:

Убедитесь, что в `bot/bot.py` или `handlers/start.py` есть кнопка для открытия WebApp:

```python
from aiogram.types import WebAppInfo

# Кнопка для открытия WebApp
web_app_button = KeyboardButton(
    text="Открыть приложение",
    web_app=WebAppInfo(url="https://your-app.vercel.app")
)
```

### В WebApp (фронт):

В `static/js/app.js` уже есть:

```javascript
const tg = window.Telegram?.WebApp;
if (tg) {
    tg.expand();
    // ...
}

// Получение telegram_id
const telegramUser = tg?.initDataUnsafe?.user;
const telegramId = telegramUser?.id;
```

### Проверка:

1. Откройте WebApp через бота (не в браузере)
2. Откройте DevTools → Network
3. Найдите запрос к `/api/user/{telegram_id}`
4. Должен быть **200 OK**
5. В ответе должен быть `referral_code`

Если падает - проверьте `DATABASE_URL` и логи Vercel.

---

## 3. Реферальная ссылка

### Как это работает:

1. **Пользователь заходит** → бэк создает/находит пользователя
2. **Генерируется referral_code** (например: `abc123`)
3. **Фронт собирает ссылку:**
   ```javascript
   const webappUrl = window.WEBAPP_URL || window.location.origin;
   referralLink = `${webappUrl}?ref=${referralCode}`;
   ```
4. **QR-код:**
   - Бэк берет `WEBAPP_URL` из настроек
   - Делает `WEBAPP_URL?ref=код`
   - Кодирует в PNG

### Новый пользователь:

1. Переходит по ссылке: `https://your-domain?ref=abc123`
2. Два варианта:
   - Открывается WebApp с кнопкой "Открыть в Telegram"
   - Или редирект на бота: `https://t.me/YOUR_BOT?start=abc123`
3. Бот ловит `/start abc123` и сохраняет привязку

### Важно:

После установки `WEBAPP_URL=https://your-domain` в Vercel:
- Фронт будет использовать этот домен
- QR-код будет использовать этот домен
- Всё будет единообразно

---

## 4. QR-код и проверка

### ⚠️ КРИТИЧНО: Проверка health перед использованием

**Перед тем как жать "Сгенерировать", обязательно проверьте:**

Откройте в браузере:
```
https://your-app.vercel.app/api/health
```

**Ожидаемый ответ (JSON):**
```json
{
  "status": "ok",
  "database": "connected",
  "api": "ok"
}
```

**Если видите HTML-страницу Vercel "Internal Server Error":**
- ❌ Backend не стартанул
- ❌ Проверьте Environment Variables (скорее всего отсутствует `BOT_TOKEN` или `DATABASE_URL`)
- ❌ Проверьте логи в Vercel → Deployments → Functions / Logs
- ❌ Перезадеплойте после добавления переменных

**Только после того, как `/api/health` возвращает JSON, можно использовать генерацию!**

### Проверка QR:

Откройте:
```
https://your-app.vercel.app/api/referral/qr?telegram_id=123456789
```

Замените `123456789` на реальный telegram_id.

Браузер должен:
- Показать PNG изображение
- Или предложить скачать

### Проверка QR ссылки:

1. Скачайте PNG
2. Отсканируйте QR-код
3. Ссылка должна быть: `https://your-domain?ref=код`

Если ссылка ведет на `https://facy-app.vercel.app`:
- `WEBAPP_URL` не задан или задан неправильно
- Проверьте переменные окружения в Vercel

---

## 5. Отладка Vercel

### Где смотреть логи:

1. **Vercel Dashboard** → ваш проект
2. **Deployments** → выберите последний деплой
3. **Functions** / **Logs**

### Частые ошибки:

**ValidationError: BOT_TOKEN is required**
- ❌ `BOT_TOKEN` не добавлен в Environment Variables
- ✅ Добавьте `BOT_TOKEN` и перезадеплойте
- ⚠️ Без этого приложение вообще не стартует!

**ValueError: DATABASE_URL not set**
- ❌ `DATABASE_URL` не добавлен в Environment Variables
- ✅ Добавьте `DATABASE_URL` в формате `postgresql+asyncpg://...` и перезадеплойте
- ⚠️ Без этого приложение вообще не стартует!

**Ошибка подключения к Postgres**
- Проверьте connection string
- Убедитесь, что база данных запущена
- Проверьте, что IP не заблокирован

**API отвечает 500 с HTML вместо JSON**
- ❌ FastAPI не стартанул из-за отсутствующих переменных
- ✅ Проверьте `/api/health` - должен возвращать JSON, а не HTML
- ✅ Проверьте логи Vercel - там будет точная ошибка
- ✅ Убедитесь, что все обязательные переменные добавлены

**Окно "ПОДТВЕРДИТЕ ДЕЙСТВИЕ НА ... Ошибка сервера:"**
- Это системное окно браузера, которое появляется когда сервер возвращает HTML вместо JSON
- Причина: FastAPI не стартанул, Vercel отдает свою HTML-страницу 500
- Решение: добавить все обязательные переменные и перезадеплоить

---

## 6. Структура проекта

### Проверка:

Убедитесь, что:
- `.git` находится в корне проекта
- `vercel.json` находится в корне проекта
- Нет дубликатов папок `api/`, `static/`, `templates/`

### Правильная структура:

```
telegram-deepface-app/  (корень)
├── .git/
├── api/
├── database/
├── static/
├── templates/
├── vercel.json
├── config.py
├── main.py
└── ...
```

### В Cursor:

1. Откройте **одну корневую папку** проекта
2. Там где реально лежат `api/`, `static/`, `vercel.json`
3. Уберите дубликаты папок
4. Cursor работает только с тем, что открыт как workspace

---

## 7. Чеклист перед деплоем

- [ ] Все переменные из `ENV_EXAMPLE.txt` добавлены в Vercel
- [ ] `DATABASE_URL` в формате `postgresql+asyncpg://...`
- [ ] `WEBAPP_URL` установлен на ваш домен
- [ ] `BOT_TOKEN` установлен
- [ ] `REPLICATE_API_KEY` установлен
- [ ] В BotFather настроен Menu Button с URL WebApp
- [ ] Проект перезадеплоен
- [ ] Проверен `/api/health` → `database: "connected"`
- [ ] Проверен `/api/referral/qr?telegram_id=...` → возвращает PNG
- [ ] QR-код ведет на правильный домен

---

## 8. Быстрая настройка (копипаста)

### В Vercel Environment Variables добавьте:

```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_DB2lLYWyVSv5@ep-sweet-thunder-a45uh81b-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require

WEBAPP_URL=https://your-app.vercel.app

BOT_TOKEN=your_token

REPLICATE_API_KEY=your_key

REPLICATE_IMAGE_MODEL=ideogram-ai/ideogram-v3-turbo

REPLICATE_VIDEO_MODEL=minimax/video-01

IMAGE_GENERATION_PROVIDER=replicate

VIDEO_GENERATION_PROVIDER=replicate

ENVIRONMENT=production
```

### После этого:

1. **Redeploy** проект
2. Проверьте `/api/health`
3. Проверьте WebApp через бота
4. Проверьте реферальную ссылку и QR

---

## Готово!

После выполнения всех шагов:
- ✅ API будет работать
- ✅ База данных подключена
- ✅ Реферальные ссылки правильные
- ✅ QR-коды работают
- ✅ Telegram Mini App работает

