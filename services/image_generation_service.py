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
        self.openai_key = settings.OPENAI_API_KEY
        self.provider = settings.IMAGE_GENERATION_PROVIDER
    
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
            model: Модель для генерации (dall-e-3, flux, sdxl, etc.)
            style: Стиль изображения
            negative_prompt: Негативный промпт
            width: Ширина изображения
            height: Высота изображения
            
        Returns:
            Результат генерации
        """
        try:
            logger.info(f"Generating image with provider: {self.provider}, has_openai_key: {bool(self.openai_key)}, has_ffans_key: {bool(self.api_key)}")
            
            # Используем OpenAI DALL-E если доступен и выбран как провайдер
            if self.openai_key and self.provider == "openai":
                logger.info("Using OpenAI DALL-E for image generation")
                return await self._generate_with_openai(prompt, model, width, height)
            
            # Используем FFans API если доступен
            if self.api_key and self.provider == "ffans":
                logger.info("Using FFans API for image generation")
                return await self._generate_with_ffans(prompt, model, style, negative_prompt, width, height)
            
            # Если OpenAI ключ есть, но провайдер не указан или указан другой - используем OpenAI
            if self.openai_key:
                logger.info("OpenAI key found, using OpenAI DALL-E as fallback")
                return await self._generate_with_openai(prompt, model, width, height)
            
            # Fallback на mock
            logger.warning("No API keys configured, using mock response")
            return {
                "status": "success",
                "message": "Mock: Image generation completed",
                "images": ["https://via.placeholder.com/1024x1024?text=Mock+Image"],
                "task_id": "mock_img_task_123"
            }
        
        except Exception as e:
            logger.error(f"Error in generate_image: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _generate_with_openai(self, prompt: str, model: str, width: int, height: int) -> Dict[str, Any]:
        """Генерация через OpenAI DALL-E"""
        try:
            # Определяем размер для DALL-E (поддерживает только определенные размеры)
            size_map = {
                (1024, 1024): "1024x1024",
                (1792, 1024): "1792x1024",
                (1024, 1792): "1024x1792"
            }
            size = size_map.get((width, height), "1024x1024")
            
            # Используем DALL-E 3
            dall_e_model = "dall-e-3" if "dall-e" in model.lower() else "dall-e-3"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.openai_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    "model": dall_e_model,
                    "prompt": prompt,
                    "size": size,
                    "quality": "standard",
                    "n": 1
                }
                
                async with session.post(
                    "https://api.openai.com/v1/images/generations",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "data" in result and len(result["data"]) > 0:
                            image_url = result["data"][0].get("url", "")
                            return {
                                "status": "success",
                                "message": "Image generated successfully",
                                "images": [image_url],
                                "task_id": result.get("created", "")
                            }
                        else:
                            return {
                                "status": "error",
                                "message": "No image data in response"
                            }
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {error_text}")
                        return {
                            "status": "error",
                            "message": f"OpenAI API error: {error_text}"
                        }
        except Exception as e:
            logger.error(f"Error in OpenAI generation: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _generate_with_ffans(self, prompt: str, model: str, style: Optional[str], 
                                   negative_prompt: Optional[str], width: int, height: int) -> Dict[str, Any]:
        """Генерация через FFans API"""
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

