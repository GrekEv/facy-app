# Использование API клиента

Скрипт `api_client.py` позволяет работать с API приложения для генерации изображений и видео.

## Установка зависимостей

Убедитесь, что установлены необходимые библиотеки:

```bash
pip install aiohttp
```

## Базовое использование

### 1. Проверка доступности API

```bash
python api_client.py health
```

Или с указанием URL:

```bash
python api_client.py --base-url https://your-api-domain.com health
```

### 2. Генерация изображения

```bash
python api_client.py image \
  --telegram-id 123456789 \
  --prompt "Красивый закат над морем, реалистичное фото"
```

С дополнительными параметрами:

```bash
python api_client.py image \
  --telegram-id 123456789 \
  --prompt "Портрет девушки в стиле аниме" \
  --model flux \
  --style anime \
  --width 1024 \
  --height 1024
```

Скачать изображение автоматически:

```bash
python api_client.py image \
  --telegram-id 123456789 \
  --prompt "Космический корабль" \
  --download \
  --output ./downloads
```

### 3. Генерация видео

```bash
python api_client.py video \
  --telegram-id 123456789 \
  --prompt "Кот играет с мячом в парке"
```

С дополнительными параметрами:

```bash
python api_client.py video \
  --telegram-id 123456789 \
  --prompt "Город будущего, летающие машины" \
  --model runway \
  --duration 10 \
  --fps 30 \
  --width 1920 \
  --height 1080
```

### 4. Проверка статуса генерации видео

После запуска генерации видео вы получите `task_id`. Используйте его для проверки статуса:

```bash
python api_client.py status --task-id task_123456
```

### 5. Получение информации о пользователе

```bash
python api_client.py user --telegram-id 123456789
```

### 6. Скачивание файла

```bash
python api_client.py download \
  --url /generated/video_123.mp4 \
  --output ./downloads/video.mp4
```

Или с полным URL:

```bash
python api_client.py download \
  --url https://your-api-domain.com/generated/video_123.mp4 \
  --output ./downloads/video.mp4
```

### 7. Получение списка моделей

Для изображений:

```bash
python api_client.py models --type image
```

Для видео:

```bash
python api_client.py models --type video
```

## Переменные окружения

Вы можете установить базовый URL API через переменную окружения:

```bash
export API_BASE_URL=https://your-api-domain.com
python api_client.py health
```

## Примеры использования в Python коде

```python
import asyncio
from api_client import APIClient

async def main():
    async with APIClient(base_url="http://localhost:8000") as client:
        # Проверка доступности
        if not await client.health_check():
            print("API недоступен")
            return
        
        # Генерация изображения
        result = await client.generate_image(
            telegram_id=123456789,
            prompt="Красивый пейзаж",
            model="flux"
        )
        
        if result.get("success"):
            image_url = result.get("image_url")
            print(f"Изображение готово: {image_url}")
            
            # Скачивание изображения
            await client.download_file(
                image_url,
                Path("./downloads/image.png")
            )
        
        # Генерация видео
        video_result = await client.generate_video(
            telegram_id=123456789,
            prompt="Кот играет с мячом",
            model="runway"
        )
        
        if video_result.get("success"):
            task_id = video_result.get("task_id")
            
            # Проверка статуса каждые 5 секунд
            while True:
                status = await client.check_video_task_status(task_id)
                if status.get("status") == "completed":
                    print(f"Видео готово: {status.get('video_url')}")
                    break
                elif status.get("status") == "failed":
                    print("Ошибка генерации видео")
                    break
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
```

## Параметры команд

### Генерация изображения (`image`)

- `--telegram-id` (обязательно) - ID пользователя Telegram
- `--prompt` (обязательно) - Текстовое описание изображения
- `--model` - Модель для генерации (по умолчанию: `flux`)
- `--style` - Стиль изображения (опционально)
- `--negative-prompt` - Негативный промпт (опционально)
- `--width` - Ширина изображения (по умолчанию: 1024)
- `--height` - Высота изображения (по умолчанию: 1024)
- `--download` - Автоматически скачать изображение
- `--output` - Директория для сохранения (по умолчанию: `./downloads`)

### Генерация видео (`video`)

- `--telegram-id` (обязательно) - ID пользователя Telegram
- `--prompt` (обязательно) - Текстовое описание видео
- `--model` - Модель для генерации (по умолчанию: `runway`)
- `--style` - Стиль видео (опционально)
- `--negative-prompt` - Негативный промпт (опционально)
- `--duration` - Длительность в секундах (по умолчанию: 5)
- `--fps` - Кадров в секунду (по умолчанию: 24)
- `--width` - Ширина видео (по умолчанию: 1280)
- `--height` - Высота видео (по умолчанию: 720)

### Проверка статуса (`status`)

- `--task-id` (обязательно) - ID задачи генерации видео

### Информация о пользователе (`user`)

- `--telegram-id` (обязательно) - ID пользователя Telegram

### Скачивание файла (`download`)

- `--url` (обязательно) - URL файла (может быть относительным)
- `--output` (обязательно) - Путь для сохранения файла

### Список моделей (`models`)

- `--type` - Тип моделей: `image` или `video` (по умолчанию: `image`)

## Обработка ошибок

Скрипт автоматически обрабатывает ошибки и выводит понятные сообщения:

- ✅ Успешные операции отображаются зеленым цветом
- ❌ Ошибки отображаются красным цветом
- ⚠️ Предупреждения отображаются желтым цветом
- ℹ️ Информационные сообщения отображаются синим цветом

## Примечания

1. Убедитесь, что API сервер запущен и доступен
2. Для генерации видео процесс может занять некоторое время - используйте команду `status` для проверки прогресса
3. Файлы сохраняются в директорию `downloads` по умолчанию (создается автоматически)
4. Все запросы асинхронные и не блокируют выполнение


