# Архитектура сервера

## Что развернуто на сервере

На сервере `72.56.85.215` развернуто **полное приложение** (фронтенд + бэкенд):

### Бэкенд (API)
- FastAPI приложение на порту 8000
- API эндпоинты: `/api/*`
- База данных SQLite
- Telegram бот

### Фронтенд
- HTML шаблон: `templates/index.html` (отдается через `/`)
- Статические файлы: `static/*` (CSS, JS, изображения)
- Все отдается через FastAPI

## Как это работает

```
Пользователь → onlyface.art → Nginx (порт 80/443) → FastAPI (порт 8000)
                                                      ↓
                                            ┌─────────┴─────────┐
                                            ↓                   ↓
                                    Фронтенд (HTML)      Бэкенд (API)
                                    /                      /api/*
                                    /static/*             /api/user/*
```

## Структура на сервере

```
~/facy-app/
├── api/              # Бэкенд (FastAPI)
│   └── main.py       # Отдает HTML и API
├── templates/        # Фронтенд (HTML)
│   └── index.html
├── static/           # Статические файлы
│   ├── css/
│   ├── js/
│   └── images/
├── bot/              # Telegram бот
├── docker-compose.prod.yml
└── .env
```

## Docker контейнеры

1. **facy-api** - FastAPI (фронтенд + бэкенд)
   - Порт: 8000
   - Отдает HTML, статику и API

2. **facy-bot** - Telegram бот
   - Подключается к API

## Nginx конфигурация

Nginx проксирует все запросы на FastAPI:

```nginx
location / {
    proxy_pass http://localhost:8000;  # Все идет в FastAPI
}

location /static/ {
    alias /path/to/static/;  # Статика отдается напрямую
}
```

## Итого

**На сервере развернуто ВСЁ:**
- ✅ Фронтенд (HTML, CSS, JS)
- ✅ Бэкенд (API)
- ✅ Telegram бот
- ✅ База данных

Все работает через один FastAPI сервер на порту 8000.

