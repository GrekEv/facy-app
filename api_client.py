#!/usr/bin/env python3
"""
Клиентский скрипт для работы с API приложения
Позволяет генерировать изображения и видео, получать результаты
"""
import asyncio
import aiohttp
import argparse
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json

# Цвета для вывода
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color


class APIClient:
    """Клиент для работы с API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Инициализация клиента
        
        Args:
            base_url: Базовый URL API сервера
        """
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        if self.session:
            await self.session.close()
    
    def _print_success(self, message: str):
        """Вывести сообщение об успехе"""
        print(f"{GREEN}[OK] {message}{NC}")
    
    def _print_error(self, message: str):
        """Вывести сообщение об ошибке"""
        print(f"{RED}[ERROR] {message}{NC}")
    
    def _print_info(self, message: str):
        """Вывести информационное сообщение"""
        print(f"{BLUE}[INFO] {message}{NC}")
    
    def _print_warning(self, message: str):
        """Вывести предупреждение"""
        print(f"{YELLOW}[WARN] {message}{NC}")
    
    async def generate_image(
        self,
        telegram_id: int,
        prompt: str,
        model: str = "flux",
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, Any]:
        """
        Генерировать изображение
        
        Args:
            telegram_id: ID пользователя Telegram
            prompt: Текстовое описание изображения
            model: Модель для генерации
            style: Стиль изображения
            negative_prompt: Негативный промпт
            width: Ширина изображения
            height: Высота изображения
            
        Returns:
            Результат генерации
        """
        self._print_info(f"Генерация изображения: {prompt[:50]}...")
        
        url = f"{self.base_url}/api/generate/image"
        payload = {
            "telegram_id": telegram_id,
            "prompt": prompt,
            "model": model,
            "width": width,
            "height": height
        }
        
        if style:
            payload["style"] = style
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        self._print_success(f"Изображение сгенерировано!")
                        self._print_info(f"URL: {result.get('image_url')}")
                        return result
                    else:
                        self._print_error(f"Ошибка: {result.get('message', 'Unknown error')}")
                        return result
                else:
                    error_text = await response.text()
                    self._print_error(f"HTTP {response.status}: {error_text}")
                    return {"success": False, "message": error_text}
        except Exception as e:
            self._print_error(f"Ошибка запроса: {e}")
            return {"success": False, "message": str(e)}
    
    async def generate_video(
        self,
        telegram_id: int,
        prompt: str,
        model: str = "runway",
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        duration: int = 5,
        fps: int = 24,
        width: int = 1280,
        height: int = 720
    ) -> Dict[str, Any]:
        """
        Генерировать видео
        
        Args:
            telegram_id: ID пользователя Telegram
            prompt: Текстовое описание видео
            model: Модель для генерации
            style: Стиль видео
            negative_prompt: Негативный промпт
            duration: Длительность в секундах
            fps: Кадров в секунду
            width: Ширина видео
            height: Высота видео
            
        Returns:
            Результат генерации
        """
        self._print_info(f"Генерация видео: {prompt[:50]}...")
        
        url = f"{self.base_url}/api/generate/video"
        payload = {
            "telegram_id": telegram_id,
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "fps": fps,
            "width": width,
            "height": height
        }
        
        if style:
            payload["style"] = style
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        self._print_success(f"Генерация видео запущена!")
                        if result.get("video_url"):
                            self._print_info(f"URL: {result.get('video_url')}")
                        if result.get("task_id"):
                            self._print_info(f"Task ID: {result.get('task_id')}")
                        return result
                    else:
                        self._print_error(f"Ошибка: {result.get('message', 'Unknown error')}")
                        return result
                else:
                    error_text = await response.text()
                    self._print_error(f"HTTP {response.status}: {error_text}")
                    return {"success": False, "message": error_text}
        except Exception as e:
            self._print_error(f"Ошибка запроса: {e}")
            return {"success": False, "message": str(e)}
    
    async def check_video_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Проверить статус задачи генерации видео
        
        Args:
            task_id: ID задачи
            
        Returns:
            Статус задачи
        """
        url = f"{self.base_url}/api/video/task/{task_id}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    status = result.get("status", "unknown")
                    progress = result.get("progress", 0)
                    
                    if status == "completed":
                        self._print_success(f"Видео готово! Прогресс: {progress}%")
                        if result.get("video_url"):
                            self._print_info(f"URL: {result.get('video_url')}")
                    elif status == "processing":
                        self._print_info(f"Обработка... Прогресс: {progress}%")
                    elif status == "failed":
                        self._print_error(f"Ошибка: {result.get('message', 'Unknown error')}")
                    else:
                        self._print_warning(f"Статус: {status}")
                    
                    return result
                else:
                    error_text = await response.text()
                    self._print_error(f"HTTP {response.status}: {error_text}")
                    return {"status": "error", "message": error_text}
        except Exception as e:
            self._print_error(f"Ошибка запроса: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_user_info(self, telegram_id: int) -> Dict[str, Any]:
        """
        Получить информацию о пользователе
        
        Args:
            telegram_id: ID пользователя Telegram
            
        Returns:
            Информация о пользователе
        """
        url = f"{self.base_url}/api/user/{telegram_id}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    self._print_success("Информация о пользователе получена")
                    return result
                else:
                    error_text = await response.text()
                    self._print_error(f"HTTP {response.status}: {error_text}")
                    return {}
        except Exception as e:
            self._print_error(f"Ошибка запроса: {e}")
            return {}
    
    async def get_models(self) -> Dict[str, Any]:
        """Получить список доступных моделей для изображений"""
        url = f"{self.base_url}/api/models"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return {"models": []}
        except Exception as e:
            self._print_error(f"Ошибка запроса: {e}")
            return {"models": []}
    
    async def get_video_models(self) -> Dict[str, Any]:
        """Получить список доступных моделей для видео"""
        url = f"{self.base_url}/api/video/models"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return {"models": []}
        except Exception as e:
            self._print_error(f"Ошибка запроса: {e}")
            return {"models": []}
    
    async def download_file(self, url: str, output_path: Path) -> bool:
        """
        Скачать файл по URL
        
        Args:
            url: URL файла (может быть относительным или абсолютным)
            output_path: Путь для сохранения файла
            
        Returns:
            True если успешно
        """
        # Если URL относительный, добавляем базовый URL
        if url.startswith('/'):
            url = f"{self.base_url}{url}"
        
        self._print_info(f"Скачивание файла: {url}")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    # Создаем директорию если нужно
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Сохраняем файл
                    with open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    self._print_success(f"Файл сохранен: {output_path}")
                    return True
                else:
                    self._print_error(f"HTTP {response.status}: Не удалось скачать файл")
                    return False
        except Exception as e:
            self._print_error(f"Ошибка скачивания: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Проверить доступность API"""
        url = f"{self.base_url}/health"
        
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "healthy":
                        self._print_success("API доступен")
                        return True
                    else:
                        self._print_warning(f"API вернул: {result}")
                        return False
                else:
                    self._print_error(f"HTTP {response.status}")
                    return False
        except asyncio.TimeoutError:
            self._print_error("Таймаут подключения к API")
            return False
        except Exception as e:
            self._print_error(f"Ошибка подключения: {e}")
            return False


async def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(
        description="Клиент для работы с API генерации изображений и видео",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Генерация изображения
  python api_client.py image --telegram-id 123456789 --prompt "Красивый закат над морем"

  # Генерация видео
  python api_client.py video --telegram-id 123456789 --prompt "Кот играет с мячом"

  # Проверка статуса видео
  python api_client.py status --task-id task_123

  # Получение информации о пользователе
  python api_client.py user --telegram-id 123456789

  # Скачивание файла
  python api_client.py download --url /generated/video.mp4 --output ./downloads/video.mp4

  # Проверка доступности API
  python api_client.py health
        """
    )
    
    parser.add_argument(
        '--base-url',
        default=os.getenv('API_BASE_URL', 'http://localhost:8000'),
        help='Базовый URL API (по умолчанию: http://localhost:8000)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    
    # Команда генерации изображения
    image_parser = subparsers.add_parser('image', help='Генерировать изображение')
    image_parser.add_argument('--telegram-id', type=int, required=True, help='ID пользователя Telegram')
    image_parser.add_argument('--prompt', required=True, help='Текстовое описание изображения')
    image_parser.add_argument('--model', default='flux', help='Модель (по умолчанию: flux)')
    image_parser.add_argument('--style', help='Стиль изображения')
    image_parser.add_argument('--negative-prompt', help='Негативный промпт')
    image_parser.add_argument('--width', type=int, default=1024, help='Ширина (по умолчанию: 1024)')
    image_parser.add_argument('--height', type=int, default=1024, help='Высота (по умолчанию: 1024)')
    image_parser.add_argument('--download', action='store_true', help='Скачать изображение')
    image_parser.add_argument('--output', type=Path, default=Path('./downloads'), help='Директория для сохранения')
    
    # Команда генерации видео
    video_parser = subparsers.add_parser('video', help='Генерировать видео')
    video_parser.add_argument('--telegram-id', type=int, required=True, help='ID пользователя Telegram')
    video_parser.add_argument('--prompt', required=True, help='Текстовое описание видео')
    video_parser.add_argument('--model', default='runway', help='Модель (по умолчанию: runway)')
    video_parser.add_argument('--style', help='Стиль видео')
    video_parser.add_argument('--negative-prompt', help='Негативный промпт')
    video_parser.add_argument('--duration', type=int, default=5, help='Длительность в секундах (по умолчанию: 5)')
    video_parser.add_argument('--fps', type=int, default=24, help='Кадров в секунду (по умолчанию: 24)')
    video_parser.add_argument('--width', type=int, default=1280, help='Ширина (по умолчанию: 1280)')
    video_parser.add_argument('--height', type=int, default=720, help='Высота (по умолчанию: 720)')
    
    # Команда проверки статуса
    status_parser = subparsers.add_parser('status', help='Проверить статус задачи генерации видео')
    status_parser.add_argument('--task-id', required=True, help='ID задачи')
    
    # Команда получения информации о пользователе
    user_parser = subparsers.add_parser('user', help='Получить информацию о пользователе')
    user_parser.add_argument('--telegram-id', type=int, required=True, help='ID пользователя Telegram')
    
    # Команда скачивания файла
    download_parser = subparsers.add_parser('download', help='Скачать файл')
    download_parser.add_argument('--url', required=True, help='URL файла (может быть относительным)')
    download_parser.add_argument('--output', type=Path, required=True, help='Путь для сохранения файла')
    
    # Команда проверки здоровья
    subparsers.add_parser('health', help='Проверить доступность API')
    
    # Команда списка моделей
    models_parser = subparsers.add_parser('models', help='Получить список моделей')
    models_parser.add_argument('--type', choices=['image', 'video'], default='image', help='Тип моделей')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    async with APIClient(base_url=args.base_url) as client:
        if args.command == 'health':
            await client.health_check()
        
        elif args.command == 'image':
            result = await client.generate_image(
                telegram_id=args.telegram_id,
                prompt=args.prompt,
                model=args.model,
                style=args.style,
                negative_prompt=args.negative_prompt,
                width=args.width,
                height=args.height
            )
            
            if result.get("success") and args.download:
                image_url = result.get("image_url")
                if image_url:
                    # Определяем имя файла
                    filename = image_url.split('/')[-1]
                    if not filename or '.' not in filename:
                        filename = f"image_{result.get('generation_id', 'unknown')}.png"
                    
                    output_path = args.output / filename
                    await client.download_file(image_url, output_path)
        
        elif args.command == 'video':
            result = await client.generate_video(
                telegram_id=args.telegram_id,
                prompt=args.prompt,
                model=args.model,
                style=args.style,
                negative_prompt=args.negative_prompt,
                duration=args.duration,
                fps=args.fps,
                width=args.width,
                height=args.height
            )
            
            if result.get("success"):
                print(f"\n{CYAN}Для проверки статуса используйте:{NC}")
                print(f"python api_client.py status --task-id {result.get('task_id')}")
        
        elif args.command == 'status':
            await client.check_video_task_status(args.task_id)
        
        elif args.command == 'user':
            result = await client.get_user_info(args.telegram_id)
            if result:
                print(f"\n{CYAN}Информация о пользователе:{NC}")
                print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.command == 'download':
            await client.download_file(args.url, args.output)
        
        elif args.command == 'models':
            if args.type == 'image':
                result = await client.get_models()
            else:
                result = await client.get_video_models()
            
            if result.get("models"):
                print(f"\n{CYAN}Доступные модели ({args.type}):{NC}")
                for model in result["models"]:
                    if isinstance(model, dict):
                        print(f"  - {model.get('id', model.get('name', 'Unknown'))}: {model.get('description', '')}")
                    else:
                        print(f"  - {model}")
            else:
                print(f"{YELLOW}Модели не найдены{NC}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Прервано пользователем{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Критическая ошибка: {e}{NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


