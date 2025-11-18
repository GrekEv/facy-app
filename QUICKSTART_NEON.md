# ⚡ Быстрый старт с Neon PostgreSQL

## 🚀 За 5 минут

### 1. Создайте проект в Neon

1. Перейдите на [console.neon.tech](https://console.neon.tech/)
2. Создайте проект
3. Скопируйте Connection String из раздела **Connection Details**

### 2. Настройте DATABASE_URL

**Вариант A: Автоматическое преобразование (рекомендуется)**

Просто скопируйте строку из Neon как есть:
```bash
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
```

Проект автоматически преобразует её в формат для asyncpg! ✨

**Вариант B: Ручное преобразование**

Если хотите указать явно:
```bash
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
```

### 3. Добавьте в .env

Создайте файл `.env` в корне проекта:

```bash
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require
BOT_TOKEN=ваш_токен_бота
WEBAPP_URL=https://your-app.vercel.app
```

### 4. Проверьте подключение

```bash
python test_neon_connection.py
```

Если видите ✅ - всё готово!

### 5. Запустите приложение

```bash
python main.py
```

Таблицы создадутся автоматически при первом запуске! 🎉

---

## 📚 Подробная инструкция

См. [NEON_SETUP.md](NEON_SETUP.md) для детальной информации.

## 🆘 Проблемы?

1. Проверьте, что `DATABASE_URL` установлен: `echo $DATABASE_URL`
2. Запустите тест: `python test_neon_connection.py`
3. Проверьте логи в Neon Console → SQL Editor

