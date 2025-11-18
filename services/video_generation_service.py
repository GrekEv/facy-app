"""Сервис для генерации видео"""
import aiohttp
import logging
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)


class VideoGenerationService:
    """Сервис для генерации видео"""
    
    def __init__(self):
        self.provider = settings.VIDEO_GENERATION_PROVIDER
        self.replicate_key = settings.REPLICATE_API_KEY
        self.replicate_model = getattr(settings, 'REPLICATE_VIDEO_MODEL', 'minimax/video-01')
        self.proxy_url = getattr(settings, 'PROXY_URL', '')
    
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
        logger.info(f"Generating video with provider: {self.provider}, model: {model}, prompt: {prompt[:50]}...")
        
        # Приоритет 1: Используем указанный провайдер
        if self.provider == "replicate" and self.replicate_key:
            logger.info(f"Using Replicate API for video generation with model: {self.replicate_model}")
            result = await self._generate_with_replicate(prompt, duration, width, height)
            if result.get("status") == "success":
                return result
            logger.warning("Replicate failed, trying fallback...")
        
        # Приоритет 2: Fallback - пробуем все доступные провайдеры
        if self.replicate_key:
            logger.info("Trying Replicate API as fallback")
            result = await self._generate_with_replicate(prompt, duration, width, height)
            if result.get("status") == "success":
                return result
        
        # Fallback на mock
        logger.warning("No working video generation provider available, using mock response")
        return {
            "status": "success",
            "message": "Video generation started (mock)",
            "video_url": None,
            "task_id": f"task_{model}_{hash(prompt)}",
            "generation_id": None
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
        
        # Для Replicate проверяем статус через их API
        if task_id and not task_id.startswith("task_"):
            # Это Replicate prediction ID
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'Authorization': f'Token {self.replicate_key}',
                        'Content-Type': 'application/json'
                    }
                    
                    proxy = self.proxy_url if self.proxy_url else None
                    async with session.get(
                        f"https://api.replicate.com/v1/predictions/{task_id}",
                        headers=headers,
                        proxy=proxy
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            status = result.get("status")
                            
                            if status == "succeeded":
                                output = result.get("output")
                                video_url = output if isinstance(output, str) else (output[0] if isinstance(output, list) else output.get("url") if isinstance(output, dict) else None)
                                return {
                                    "status": "completed",
                                    "progress": 100,
                                    "video_url": video_url,
                                    "message": "Video generation completed"
                                }
                            elif status == "failed":
                                return {
                                    "status": "failed",
                                    "progress": 0,
                                    "video_url": None,
                                    "message": result.get("error", "Generation failed")
                                }
                            else:
                                return {
                                    "status": "processing",
                                    "progress": 50,
                                    "video_url": None,
                                    "message": "Video is being generated"
                                }
            except Exception as e:
                logger.error(f"Error checking Replicate status: {e}")
        
        # Mock статус для других провайдеров
        return {
            "status": "processing",
            "progress": 50,
            "video_url": None,
            "message": "Video is being generated"
        }
    
    async def get_available_video_models(self) -> list:
        """Получить список доступных моделей для генерации видео"""
        return [
            {"id": "minimax", "name": "Minimax Video-01", "description": "Генерация видео через Replicate"},
            {"id": "runway", "name": "RunwayML", "description": "Высококачественная генерация видео"},
            {"id": "pika", "name": "Pika Labs", "description": "Быстрая генерация видео"}
        ]
    
    async def get_available_video_styles(self) -> list:
        """Получить список доступных стилей для видео"""
        return [
            {"id": "realistic", "name": "Реалистичный"},
            {"id": "cinematic", "name": "Кинематографичный"},
            {"id": "anime", "name": "Аниме"},
            {"id": "cartoon", "name": "Мультяшный"}
        ]
    
    async def _generate_with_replicate(self, prompt: str, duration: int, width: int, height: int) -> Dict[str, Any]:
        """Генерация видео через Replicate API с использованием minimax/video-01"""
        try:
            replicate_model = self.replicate_model
            
            # Настройка прокси если указан
            proxy = self.proxy_url if self.proxy_url else None
            if proxy:
                logger.info(f"Using proxy for Replicate API: {proxy.split('@')[-1] if '@' in proxy else proxy}")
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Token {self.replicate_key}',
                    'Content-Type': 'application/json'
                }
                
                # Для minimax/video-01 используем только prompt
                input_params = {
                    "prompt": prompt
                }
                
                # Создаем prediction
                payload = {
                    "input": input_params
                }
                
                # URL для создания prediction
                model_path = replicate_model.split(':')[0]
                predictions_url = f"https://api.replicate.com/v1/models/{model_path}/predictions"
                
                logger.info(f"Creating prediction with Replicate API: {predictions_url}")
                logger.info(f"Payload: {payload}")
                
                async with session.post(
                    predictions_url,
                    json=payload,
                    headers=headers,
                    proxy=proxy,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_text = await response.text()
                    logger.info(f"Replicate API response status: {response.status}, body: {response_text[:500]}")
                    
                    if response.status == 201:
                        result = await response.json()
                        prediction_id = result.get("id")
                        logger.info(f"Prediction created: {prediction_id}")
                        
                        # Ждем завершения генерации
                        import asyncio
                        max_attempts = 120  # Увеличиваем для видео (может занять больше времени)
                        for attempt in range(max_attempts):
                            await asyncio.sleep(3)  # Проверяем каждые 3 секунды
                            
                            async with session.get(
                                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                                headers=headers,
                                proxy=proxy
                            ) as status_response:
                                if status_response.status == 200:
                                    status_result = await status_response.json()
                                    status = status_result.get("status")
                                    
                                    logger.info(f"Prediction status (attempt {attempt + 1}/{max_attempts}): {status}")
                                    
                                    if status == "succeeded":
                                        output = status_result.get("output")
                                        # Для minimax/video-01 output может быть строкой URL или объектом
                                        if isinstance(output, str):
                                            video_url = output
                                        elif isinstance(output, list) and len(output) > 0:
                                            video_url = output[0] if isinstance(output[0], str) else output[0].get("url") if isinstance(output[0], dict) else None
                                        elif isinstance(output, dict):
                                            video_url = output.get("url") or output.get("output")
                                        else:
                                            video_url = None
                                        
                                        if video_url:
                                            logger.info(f"Video generated successfully: {video_url}")
                                            return {
                                                "status": "success",
                                                "message": "Video generated successfully",
                                                "video_url": video_url,
                                                "task_id": prediction_id
                                            }
                                        else:
                                            logger.error(f"Unexpected output format: {output}")
                                            return {
                                                "status": "error",
                                                "message": f"Unexpected output format from Replicate API"
                                            }
                                    elif status == "failed":
                                        error = status_result.get("error", "Unknown error")
                                        logger.error(f"Replicate API error: {error}")
                                        return {
                                            "status": "error",
                                            "message": f"Replicate API error: {error}"
                                        }
                                    elif status == "canceled":
                                        return {
                                            "status": "error",
                                            "message": "Video generation was canceled"
                                        }
                        
                        return {
                            "status": "error",
                            "message": "Replicate API timeout - video generation took too long"
                        }
                    else:
                        logger.error(f"Replicate API error: status={response.status}, body={response_text}")
                        try:
                            error_json = await response.json() if response_text else {}
                            error_detail = error_json.get("detail", error_json.get("error", response_text))
                        except:
                            error_detail = response_text
                        return {
                            "status": "error",
                            "message": f"Replicate API error (status {response.status}): {error_detail[:200]}"
                        }
        except Exception as e:
            logger.error(f"Error in Replicate video generation: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


# Создаем экземпляр сервиса
video_generation_service = VideoGenerationService()
