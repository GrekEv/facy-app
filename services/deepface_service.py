"""Сервис для работы с DeepFace API"""
import aiohttp
import logging
import os
from typing import Optional, Dict, Any
from config import settings

logger = logging.getLogger(__name__)


class DeepFaceService:
    """Сервис для замены лиц в видео"""
    
    def __init__(self):
        self.api_url = settings.DEEPFACE_API_URL
        self.api_key = settings.DEEPFACE_API_KEY
    
    async def swap_face(
        self,
        source_image_path: str,
        target_video_path: str,
        output_path: str
    ) -> Dict[str, Any]:
        """
        Заменить лицо в видео
        
        Args:
            source_image_path: Путь к исходному изображению лица
            target_video_path: Путь к целевому видео
            output_path: Путь для сохранения результата
            
        Returns:
            Результат обработки
        """
        try:
            if not self.api_key:
                logger.warning("DeepFace API key not configured, using mock response")
                # В mock режиме создаем пустой файл для тестирования
                import os
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write("")  # Создаем пустой файл
                return {
                    "status": "success",
                    "message": "Mock: DeepFace processing completed",
                    "output_path": output_path,
                    "task_id": "mock_task_123"
                }
            
            # Реальный запрос к API DeepFace
            async with aiohttp.ClientSession() as session:
                # Подготавливаем файлы для отправки
                data = aiohttp.FormData()
                
                with open(source_image_path, 'rb') as f:
                    data.add_field('source_image',
                                 f,
                                 filename='source.jpg',
                                 content_type='image/jpeg')
                
                with open(target_video_path, 'rb') as f:
                    data.add_field('target_video',
                                 f,
                                 filename='target.mp4',
                                 content_type='video/mp4')
                
                headers = {
                    'Authorization': f'Bearer {self.api_key}'
                }
                
                async with session.post(
                    f"{self.api_url}/swap",
                    data=data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 минут таймаут
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Если API возвращает URL видео, скачиваем его
                        if result.get("video_url"):
                            video_url = result["video_url"]
                            async with session.get(video_url) as video_response:
                                if video_response.status == 200:
                                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                                    with open(output_path, 'wb') as f:
                                        f.write(await video_response.read())
                        
                        return {
                            "status": "success",
                            "message": result.get("message", "Face swap completed"),
                            "output_path": output_path,
                            "task_id": result.get("task_id", "")
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"DeepFace API error: {error_text}")
                        return {
                            "status": "error",
                            "message": f"API error: {error_text}"
                        }
        
        except Exception as e:
            logger.error(f"Error in swap_face: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Проверить статус задачи
        
        Args:
            task_id: ID задачи
            
        Returns:
            Статус задачи
        """
        try:
            if not self.api_key:
                return {
                    "status": "completed",
                    "progress": 100,
                    "result_url": "mock_result.mp4"
                }
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}'
                }
                
                async with session.get(
                    f"{self.api_url}/task/{task_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {
                            "status": "error",
                            "message": "Failed to check status"
                        }
        
        except Exception as e:
            logger.error(f"Error checking task status: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


deepface_service = DeepFaceService()

