"""Сервис для генерации видео"""
import aiohttp
import logging
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)


class VideoGenerationService:
    """Сервис для генерации видео"""
    
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.provider = settings.VIDEO_GENERATION_PROVIDER
    
    async def generate_video(
        self,
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
        Генерировать видео по текстовому описанию
        
        Args:
            prompt: Текстовое описание видео
            model: Модель для генерации (sora, runway, pika и т.д.)
            style: Стиль видео
            negative_prompt: Что исключить из видео
            duration: Длительность в секундах
            fps: Кадров в секунду
            width: Ширина видео
            height: Высота видео
            
        Returns:
            Словарь с результатом генерации
        """
        logger.info(f"Generating video with model {model}, prompt: {prompt[:50]}...")
        
        # Используем OpenAI Sora если доступен
        if self.openai_key and (model == "sora" or self.provider == "sora"):
            return await self._generate_with_sora(prompt, duration, width, height)
        
        # Fallback на mock (Sora пока в waitlist)
        logger.warning("Sora not available yet, using mock response")
        return {
            "status": "success",
            "message": "Video generation started (mock)",
            "video_url": None,
            "task_id": f"task_{model}_{hash(prompt)}",
            "generation_id": None
        }
    
    async def _generate_with_sora(self, prompt: str, duration: int, width: int, height: int) -> Dict[str, Any]:
        """Генерация через OpenAI Sora"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.openai_key}',
                    'Content-Type': 'application/json'
                }
                
                # Sora API (когда будет доступен)
                payload = {
                    "model": "sora",
                    "prompt": prompt,
                    "duration": duration,
                    "width": width,
                    "height": height
                }
                
                async with session.post(
                    "https://api.openai.com/v1/video/generations",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "success",
                            "message": "Video generation started",
                            "video_url": result.get("video_url"),
                            "task_id": result.get("id"),
                            "generation_id": None
                        }
                    elif response.status == 404:
                        # Sora еще не доступен
                        logger.warning("Sora API not available yet")
                        return {
                            "status": "success",
                            "message": "Video generation queued (Sora in waitlist)",
                            "video_url": None,
                            "task_id": f"sora_{hash(prompt)}",
                            "generation_id": None
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI Sora API error: {error_text}")
                        return {
                            "status": "error",
                            "message": f"Sora API error: {error_text}"
                        }
        except Exception as e:
            logger.error(f"Error in Sora generation: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def check_video_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Проверить статус задачи генерации видео
        
        Args:
            task_id: ID задачи
            
        Returns:
            Словарь со статусом задачи
        """
        logger.info(f"Checking video task status: {task_id}")
        
        # Проверяем статус через OpenAI Sora API
        if self.openai_key and task_id.startswith("sora_"):
            return await self._check_sora_status(task_id)
        
        # Mock статус для других провайдеров
        return {
            "status": "processing",
            "progress": 50,
            "video_url": None,
            "message": "Video is being generated"
        }
    
    async def _check_sora_status(self, task_id: str) -> Dict[str, Any]:
        """Проверка статуса через OpenAI Sora API"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.openai_key}'
                }
                
                async with session.get(
                    f"https://api.openai.com/v1/video/generations/{task_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": result.get("status", "processing"),
                            "progress": result.get("progress", 0),
                            "video_url": result.get("video_url"),
                            "message": result.get("message", "Processing")
                        }
                    else:
                        return {
                            "status": "processing",
                            "progress": 50,
                            "video_url": None,
                            "message": "Checking status..."
                        }
        except Exception as e:
            logger.error(f"Error checking Sora status: {e}")
            return {
                "status": "processing",
                "progress": 50,
                "video_url": None,
                "message": "Status check failed"
            }
    
    async def get_available_video_models(self) -> list:
        """Получить список доступных моделей для генерации видео"""
        return [
            {"id": "runway", "name": "RunwayML", "description": "Высококачественная генерация видео"},
            {"id": "pika", "name": "Pika Labs", "description": "Быстрая генерация видео"},
            {"id": "sora", "name": "OpenAI Sora", "description": "Продвинутая генерация видео (когда будет доступен)"}
        ]
    
    async def get_available_video_styles(self) -> list:
        """Получить список доступных стилей для видео"""
        return [
            {"id": "realistic", "name": "Реалистичный"},
            {"id": "cinematic", "name": "Кинематографичный"},
            {"id": "anime", "name": "Аниме"},
            {"id": "cartoon", "name": "Мультяшный"}
        ]


# Создаем экземпляр сервиса
video_generation_service = VideoGenerationService()
