# Исправление DATABASE_URL в .env

## Проблема
В `.env` файле DATABASE_URL имеет неправильный формат:
- Используется `postgresql://` вместо `postgresql+asyncpg://`
- Возможно, строка обрезана

## Решение

### В nano редакторе:

1. **Найдите строку DATABASE_URL:**
   - Нажмите `Ctrl+W` (поиск)
   - Введите `DATABASE_URL`
   - Нажмите Enter

2. **Удалите старую строку:**
   - Переместите курсор на начало строки `DATABASE_URL`
   - Нажмите `Ctrl+K` несколько раз, чтобы удалить всю строку

3. **Добавьте правильную строку:**
   - Переместите курсор в конец файла (или на новую строку)
   - Введите (замените пароль на ваш реальный):
   ```
   DATABASE_URL=postgresql+asyncpg://gen_user:ваш_пароль@ad9d6b1abc9d6aa538e0dea5.twc1.net:5432/default_db?ssl=require
   ```

4. **Важно:**
   - Формат: `postgresql+asyncpg://` (не просто `postgresql://`)
   - Без кавычек вокруг значения
   - Пароль должен быть реальным (скопируйте из панели Timeweb)
   - Параметр `?ssl=require` обязателен

5. **Сохраните:**
   - `Ctrl+O` (Write Out - сохранить)
   - `Enter` (подтвердить имя файла)
   - `Ctrl+X` (выйти)

### Пример правильной строки:

```
DATABASE_URL=postgresql+asyncpg://gen_user:e%7D%2B%400Go~xgGcwt@ad9d6b1abc9d6aa538e0dea5.twc1.net:5432/default_db?ssl=require
```

### После сохранения:

```bash
# Проверьте содержимое (пароль будет скрыт)
grep DATABASE_URL .env | sed 's/:[^:@]*@/:***@/'

# Перезапустите контейнеры
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

# Подождите 30 секунд
sleep 30

# Проверка
curl http://localhost:8000/api/health
```

