# Где посмотреть логи приложения

## 1. Локальный запуск (Python напрямую)

### Логи в консоли (терминале)

Если запускаете через:
```bash
python3 main.py          # Бот
python3 run_api.py       # API сервер
uvicorn api.main:app     # API сервер напрямую
```

**Логи выводятся прямо в терминал** где запущено приложение.

### Просмотр логов в реальном времени

Откройте терминал где запущено приложение - там будут все логи.

---

## 2. Запуск через скрипты

### start_local.sh
```bash
./start_local.sh
```
Логи выводятся в терминал.

### start_both.sh
```bash
./start_both.sh
```
Логи выводятся в терминал.

---

## 3. Запуск через Docker

### Просмотр логов контейнера

```bash
# Список контейнеров
docker ps

# Логи API контейнера
docker logs <container_name> -f

# Логи бота контейнера  
docker logs <container_name> -f

# Последние 100 строк логов
docker logs <container_name> --tail 100

# Логи с временными метками
docker logs <container_name> -f --timestamps
```

### Примеры

```bash
# Если контейнер называется telegram-deepface-app-api
docker logs telegram-deepface-app-api -f

# Если контейнер называется telegram-deepface-app-bot
docker logs telegram-deepface-app-bot -f
```

---

## 4. Запуск через Docker Compose

### Просмотр логов всех сервисов

```bash
# Все логи
docker-compose logs -f

# Только API
docker-compose logs -f api

# Только бот
docker-compose logs -f bot

# Последние 100 строк
docker-compose logs --tail 100
```

---

## 5. Запуск на сервере (systemd)

### Просмотр логов через journalctl

```bash
# Логи сервиса
sudo journalctl -u telegram-deepface-app -f

# Последние 100 строк
sudo journalctl -u telegram-deepface-app -n 100

# Логи за сегодня
sudo journalctl -u telegram-deepface-app --since today

# Логи с временными метками
sudo journalctl -u telegram-deepface-app -f --since "1 hour ago"
```

### Если запущено через nohup

```bash
# Проверьте файлы логов
ls -la *.log

# Просмотр лога
tail -f bot.log
tail -f api.log
```

---

## 6. Запуск на Vercel

### Просмотр логов в Vercel Dashboard

1. Откройте https://vercel.com/dashboard
2. Выберите ваш проект
3. Перейдите в **Deployments**
4. Выберите нужный деплой
5. Нажмите **Functions** → **api/index** → **View Function Logs**

Или через Vercel CLI:
```bash
vercel logs
```

---

## 7. Запуск на Railway/Render

### Railway
1. Откройте Railway Dashboard
2. Выберите проект
3. Перейдите в **Deployments**
4. Выберите деплой → **View Logs**

### Render
1. Откройте Render Dashboard
2. Выберите сервис
3. Вкладка **Logs**

---

## 8. Проверка логов генерации изображений

### В коде приложения

Логи генерации изображений выводятся через `logger.info()` в:
- `services/image_generation_service.py`
- `api/main.py`

Ищите строки:
```
Generating image with provider: openai, has_openai_key: True
Using OpenAI DALL-E for image generation
Image generation completed successfully, URL: ...
```

### В браузере (Frontend)

Откройте DevTools (F12) → **Console**:
- Там будут логи JavaScript:
  - `API_BASE_URL determined: ...`
  - `Sending request to: ...`
  - `Response status: ...`
  - `Generation successful, image_url: ...`

---

## 9. Быстрая проверка логов

### Проверка, что OpenAI ключ загружен

В логах должно быть:
```
Generating image with provider: openai, has_openai_key: True
```

Если `has_openai_key: False` - ключ не загружен из переменных окружения.

### Проверка ошибок

Ищите в логах:
- `ERROR` - ошибки
- `WARNING` - предупреждения
- `OpenAI API error` - ошибки от OpenAI API

---

## 10. Сохранение логов в файл

### При запуске через Python

```bash
# Сохранить логи в файл
python3 main.py > bot.log 2>&1
python3 run_api.py > api.log 2>&1

# Просмотр
tail -f bot.log
tail -f api.log
```

### При запуске через uvicorn

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1
```

---

## Полезные команды для поиска в логах

```bash
# Поиск ошибок
grep -i error *.log

# Поиск упоминаний OpenAI
grep -i openai *.log

# Поиск генераций изображений
grep -i "image generation" *.log

# Последние 50 строк с ошибками
tail -n 50 *.log | grep -i error
```

