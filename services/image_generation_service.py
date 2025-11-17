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
        self.openai_proxy = settings.OPENAI_PROXY
        self.replicate_key = settings.REPLICATE_API_KEY
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
            proxy_info = f", proxy: {'configured' if self.openai_proxy else 'not configured'}"
            logger.info(f"Generating image with provider: {self.provider}, has_openai_key: {bool(self.openai_key)}, has_ffans_key: {bool(self.api_key)}, has_replicate_key: {bool(self.replicate_key)}{proxy_info}")
            
            # Приоритет 1: OpenAI если доступен и выбран как провайдер
            if self.openai_key and self.provider == "openai":
                logger.info("Using OpenAI DALL-E for image generation")
                result = await self._generate_with_openai(prompt, model, width, height)
                # Если OpenAI недоступен в регионе, пробуем альтернативы
                if result.get("status") == "error" and ("unsupported_country_region_territory" in result.get("message", "") or "Ошибка подключения" in result.get("message", "")):
                    logger.warning("OpenAI недоступен, пробуем альтернативные провайдеры...")
                    if self.api_key:
                        logger.info("Trying FFans API as fallback")
                        return await self._generate_with_ffans(prompt, model, style, negative_prompt, width, height)
                    if self.replicate_key:
                        logger.info("Trying Replicate API as fallback")
                        return await self._generate_with_replicate(prompt, model, width, height)
                return result
            
            # Приоритет 2: Если провайдер не указан, используем OpenAI (основной провайдер)
            if self.openai_key and not self.provider:
                logger.info("No provider specified, using OpenAI DALL-E")
                result = await self._generate_with_openai(prompt, model, width, height)
                # Если OpenAI недоступен в регионе, пробуем альтернативы
                if result.get("status") == "error" and ("unsupported_country_region_territory" in result.get("message", "") or "Ошибка подключения" in result.get("message", "")):
                    logger.warning("OpenAI недоступен, пробуем альтернативные провайдеры...")
                    if self.api_key:
                        logger.info("Trying FFans API as fallback")
                        return await self._generate_with_ffans(prompt, model, style, negative_prompt, width, height)
                    if self.replicate_key:
                        logger.info("Trying Replicate API as fallback")
                        return await self._generate_with_replicate(prompt, model, width, height)
                return result
            
            # Приоритет 3: Альтернативные провайдеры если OpenAI недоступен
            # Используем FFans API если доступен и выбран как провайдер
            if self.api_key and self.provider == "ffans":
                logger.info("Using FFans API for image generation")
                return await self._generate_with_ffans(prompt, model, style, negative_prompt, width, height)
            
            # Используем Replicate API если доступен и выбран как провайдер
            if self.replicate_key and self.provider == "replicate":
                logger.info("Using Replicate API for image generation")
                return await self._generate_with_replicate(prompt, model, width, height)
            
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
            # DALL-E 3 поддерживает: 1024x1024, 1024x1536, 1536x1024
            size_map = {
                (1024, 1024): "1024x1024",
                (1024, 1536): "1024x1536",
                (1536, 1024): "1536x1024"
            }
            size = size_map.get((width, height), "1024x1024")
            
            # Используем DALL-E 3
            dall_e_model = "dall-e-3" if "dall-e" in model.lower() else "dall-e-3"
            
            # Настройка прокси для OpenAI API (если указан)
            proxy = self.openai_proxy if self.openai_proxy else None
            if proxy:
                logger.info(f"Using proxy for OpenAI API: {proxy.split('@')[-1] if '@' in proxy else proxy}")
            else:
                logger.info("No proxy configured for OpenAI API")
            
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
                    headers=headers,
                    proxy=proxy
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
                        
                        # Проверка на ошибку региона
                        if "unsupported_country_region_territory" in error_text:
                            if proxy:
                                logger.error(f"OpenAI API недоступен в регионе даже через прокси {proxy.split('@')[-1] if '@' in proxy else proxy}. Проверьте настройки прокси или используйте альтернативный провайдер.")
                                return {
                                    "status": "error",
                                    "message": "Ошибка подключения к сервису генерации. Попробуйте позже или используйте другую модель."
                                }
                            else:
                                logger.warning("OpenAI API недоступен в регионе сервера. Настройте OPENAI_PROXY в .env или используйте альтернативный провайдер.")
                                return {
                                    "status": "error",
                                    "message": "Ошибка подключения к сервису генерации. Попробуйте позже или используйте другую модель."
                                }
                        
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
    
    async def _generate_with_replicate(self, prompt: str, model: str, width: int, height: int) -> Dict[str, Any]:
        """Генерация через Replicate API"""
        try:
            # Выбираем модель в зависимости от запроса
            replicate_model = "black-forest-labs/flux-schnell" if "flux" in model.lower() else "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Token {self.replicate_key}',
                    'Content-Type': 'application/json'
                }
                
                # Создаем prediction
                payload = {
                    "version": replicate_model.split(":")[1] if ":" in replicate_model else None,
                    "input": {
                        "prompt": prompt,
                        "width": width,
                        "height": height
                    }
                }
                
                async with session.post(
                    f"https://api.replicate.com/v1/models/{replicate_model.split(':')[0]}/predictions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        prediction_id = result.get("id")
                        
                        # Ждем завершения генерации
                        import asyncio
                        max_attempts = 60
                        for attempt in range(max_attempts):
                            await asyncio.sleep(2)
                            
                            async with session.get(
                                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                                headers=headers
                            ) as status_response:
                                if status_response.status == 200:
                                    status_result = await status_response.json()
                                    status = status_result.get("status")
                                    
                                    if status == "succeeded":
                                        output = status_result.get("output")
                                        if isinstance(output, list) and len(output) > 0:
                                            image_url = output[0]
                                        elif isinstance(output, str):
                                            image_url = output
                                        else:
                                            image_url = None
                                        
                                        if image_url:
                                            return {
                                                "status": "success",
                                                "message": "Image generated successfully",
                                                "images": [image_url],
                                                "task_id": prediction_id
                                            }
                                    elif status == "failed":
                                        error = status_result.get("error", "Unknown error")
                                        return {
                                            "status": "error",
                                            "message": f"Replicate API error: {error}"
                                        }
                        
                        return {
                            "status": "error",
                            "message": "Replicate API timeout - generation took too long"
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Replicate API error: {error_text}")
                        return {
                            "status": "error",
                            "message": f"Replicate API error: {error_text}"
                        }
        except Exception as e:
            logger.error(f"Error in Replicate generation: {e}")
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

