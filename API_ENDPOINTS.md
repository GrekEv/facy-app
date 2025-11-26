# API Эндпоинты

## Health Check

- `GET /health` - Базовая проверка здоровья
- `GET /api/health` - Детальная проверка API и БД

## Пользователи

- `GET /api/user/{telegram_id}` - Получить данные пользователя
- `POST /api/user/{telegram_id}/activate-basic-plan` - Активировать базовый план

## Генерация изображений

- `POST /api/generate/image` - Генерация изображения
- `GET /api/models` - Список доступных моделей
- `GET /api/styles` - Список доступных стилей

## Генерация видео

- `POST /api/generate/video` - Генерация видео
- `GET /api/video/models` - Список моделей для видео
- `GET /api/video/styles` - Список стилей для видео
- `GET /api/video/task/{task_id}` - Проверка статуса задачи генерации видео

## Deepfake

- `POST /api/deepfake/swap` - Замена лица в видео
- `GET /api/deepfake/task/{task_id}` - Проверка статуса задачи deepfake

## Утилиты

- `POST /api/remove-background` - Удаление фона с изображения
- `GET /api/referral/qr` - Генерация QR-кода реферальной ссылки
- `GET /api/stats` - Статистика системы

## Аутентификация

- `POST /api/auth/send-verification-code` - Отправка кода верификации email
- `POST /api/auth/verify-email-code` - Проверка кода верификации email

## Платежи

- Роуты из `api/payments.py` (подключаются автоматически)

## Статические файлы

- `/static/*` - Статические файлы
- `/uploads/*` - Загруженные файлы
- `/generated/*` - Сгенерированные файлы

## Проверка API

```bash
# Локально
curl http://localhost:8000/health
curl http://localhost:8000/api/health

# На сервере
curl http://72.56.85.215:8000/health
curl http://72.56.85.215:8000/api/health

# Через домен (после настройки)
curl https://onlyface.art/health
curl https://onlyface.art/api/health
```

Или используйте скрипт:
```bash
./check_api.sh http://localhost:8000
./check_api.sh https://onlyface.art
```

