"""Сервис для генерации изображений"""
import aiohttp
import logging
from typing import Optional, Dict, Any, List
from config import settings

logger = logging.getLogger(__name__)


class ImageGenerationService:
    """Сервис для генерации изображений через FFans API"""
    
    def __init__(self):
        self.api_url = settings.FFANS_API_URL
        self.api_key = settings.FFANS_API_KEY
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "flux",
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, Any]:
        """
        Генерировать изображение по текстовому описанию
        
        Args:
            prompt: Текстовое описание желаемого изображения
            model: Модель для генерации (flux, sdxl, etc.)
            style: Стиль изображения
            negative_prompt: Негативный промпт
            width: Ширина изображения
            height: Высота изображения
            
        Returns:
            Результат генерации
        """
        try:
            if not self.api_key:
                logger.warning("FFans API key not configured, using mock response")
                return {
                    "status": "success",
                    "message": "Mock: Image generation completed",
                    "images": ["mock_image_url.png"],
                    "task_id": "mock_img_task_123"
                }
            
            # Реальный запрос к API
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    "prompt": prompt,
                    "model": model,
                    "width": width,
                    "height": height
                }
                
                if style:
                    payload["style"] = style
                
                if negative_prompt:
                    payload["negative_prompt"] = negative_prompt
                
                async with session.post(
                    f"{self.api_url}/generate",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"FFans API error: {error_text}")
                        return {
                            "status": "error",
                            "message": f"API error: {error_text}"
                        }
        
        except Exception as e:
            logger.error(f"Error in generate_image: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Получить список доступных моделей
        
        Returns:
            Список моделей
        """
        try:
            if not self.api_key:
                return [
                    {"id": "flux", "name": "FLUX", "description": "Быстрая и качественная генерация"},
                    {"id": "sdxl", "name": "Stable Diffusion XL", "description": "Высокое качество"},
                    {"id": "midjourney", "name": "Midjourney Style", "description": "Художественный стиль"}
                ]
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.api_key}'
                }
                
                async with session.get(
                    f"{self.api_url}/models",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return []
        
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []
    
    async def get_available_styles(self) -> List[Dict[str, Any]]:
        """
        Получить список доступных стилей
        
        Returns:
            Список стилей
        """
        return [
            {"id": "realistic", "name": "Реалистичный", "preview": "realistic.jpg"},
            {"id": "anime", "name": "Аниме", "preview": "anime.jpg"},
            {"id": "artistic", "name": "Художественный", "preview": "artistic.jpg"},
            {"id": "fantasy", "name": "Фэнтези", "preview": "fantasy.jpg"},
            {"id": "cyberpunk", "name": "Киберпанк", "preview": "cyberpunk.jpg"},
        ]


image_generation_service = ImageGenerationService()

