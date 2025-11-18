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
        self.replicate_key = settings.REPLICATE_API_KEY
        self.provider = settings.IMAGE_GENERATION_PROVIDER
        self.replicate_model = getattr(settings, 'REPLICATE_IMAGE_MODEL', 'ideogram-ai/ideogram-v3-turbo')
        self.proxy_url = getattr(settings, 'PROXY_URL', '')
    
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
            logger.info(f"Generating image with provider: {self.provider}, has_ffans_key: {bool(self.api_key)}, has_replicate_key: {bool(self.replicate_key)}")
            
            # Приоритет 1: Используем указанный провайдер
            if self.provider == "replicate" and self.replicate_key:
                logger.info(f"Using Replicate API for image generation with model: {self.replicate_model}")
                result = await self._generate_with_replicate(prompt, model, width, height, style)
                if result.get("status") == "success":
                    return result
                logger.warning("Replicate failed, trying fallback...")
            
            if self.provider == "ffans" and self.api_key:
                logger.info("Using FFans API for image generation")
                result = await self._generate_with_ffans(prompt, model, style, negative_prompt, width, height)
                if result.get("status") == "success":
                    return result
                logger.warning("FFans failed, trying fallback...")
            
            # Приоритет 2: Fallback - пробуем все доступные провайдеры по порядку
            if self.replicate_key:
                logger.info("Trying Replicate API as fallback")
                result = await self._generate_with_replicate(prompt, model, width, height, style)
                if result.get("status") == "success":
                    return result
            
            if self.api_key:
                logger.info("Trying FFans API as fallback")
                result = await self._generate_with_ffans(prompt, model, style, negative_prompt, width, height)
                if result.get("status") == "success":
                    return result
            
            # Fallback на mock
            logger.warning("No working API available, using mock response")
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
    
    async def _generate_with_replicate(self, prompt: str, model: str, width: int, height: int, style: Optional[str] = None, aspect_ratio: Optional[str] = None) -> Dict[str, Any]:
        """Генерация через Replicate API с использованием ideogram-v3-turbo"""
        try:
            # Используем ideogram-v3-turbo по умолчанию
            replicate_model = self.replicate_model
            
            # Определяем aspect_ratio на основе width и height для ideogram
            if not aspect_ratio:
                if width == height:
                    aspect_ratio = "1:1"
                elif width > height:
                    ratio = width / height
                    if ratio >= 1.7:
                        aspect_ratio = "16:9"
                    elif ratio >= 1.4:
                        aspect_ratio = "3:2"
                    else:
                        aspect_ratio = "4:3"
                else:
                    ratio = height / width
                    if ratio >= 1.7:
                        aspect_ratio = "9:16"
                    elif ratio >= 1.4:
                        aspect_ratio = "2:3"
                    else:
                        aspect_ratio = "3:4"
            
            # Настройка прокси если указан
            proxy = self.proxy_url if self.proxy_url else None
            if proxy:
                logger.info(f"Using proxy for Replicate API: {proxy.split('@')[-1] if '@' in proxy else proxy}")
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Token {self.replicate_key}',
                    'Content-Type': 'application/json',
                    'Prefer': 'wait'  # Ждем завершения генерации (как в официальной инструкции)
                }
                
                # Для ideogram-v3-turbo используем параметры согласно официальной инструкции
                if "ideogram" in replicate_model.lower():
                    input_params = {
                        "prompt": prompt,
                        "aspect_ratio": aspect_ratio,
                        "resolution": "None",  # Можно указать конкретное разрешение или None
                        "style_type": "None",  # Можно указать стиль или None
                        "style_preset": "None",  # Можно указать пресет стиля или None
                        "magic_prompt_option": "Auto"  # Автоматическое улучшение промпта
                    }
                else:
                    # Для других моделей используем width/height
                    input_params = {
                        "prompt": prompt,
                        "width": width,
                        "height": height
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
                        
                        # Ждем завершения генерации
                        import asyncio
                        max_attempts = 60
                        for attempt in range(max_attempts):
                            await asyncio.sleep(2)
                            
                            async with session.get(
                                f"https://api.replicate.com/v1/predictions/{prediction_id}",
                                headers=headers,
                                proxy=proxy
                            ) as status_response:
                                if status_response.status == 200:
                                    status_result = await status_response.json()
                                    status = status_result.get("status")
                                    
                                    if status == "succeeded":
                                        output = status_result.get("output")
                                        logger.info(f"Replicate output type: {type(output)}, value: {output}")
                                        
                                        # Для ideogram-v3-turbo output может быть:
                                        # 1. Строкой URL напрямую
                                        # 2. Списком с URL
                                        # 3. Объектом с методом url() (в Node.js SDK)
                                        # 4. Словарем с ключом url
                                        
                                        image_url = None
                                        if isinstance(output, str):
                                            image_url = output
                                        elif isinstance(output, list):
                                            if len(output) > 0:
                                                if isinstance(output[0], str):
                                                    image_url = output[0]
                                                elif isinstance(output[0], dict):
                                                    image_url = output[0].get("url") or output[0].get("output")
                                        elif isinstance(output, dict):
                                            # Проверяем разные возможные ключи
                                            image_url = (
                                                output.get("url") or 
                                                output.get("output") or
                                                output.get("image_url") or
                                                output.get("file")
                                            )
                                        
                                        # Если все еще None, логируем для отладки
                                        if not image_url:
                                            logger.error(f"Could not extract image URL from output: {output}")
                                            logger.error(f"Output type: {type(output)}, keys: {output.keys() if isinstance(output, dict) else 'N/A'}")
                                        
                                        if image_url:
                                            logger.info(f"Image generated successfully: {image_url}")
                                            return {
                                                "status": "success",
                                                "message": "Image generated successfully",
                                                "images": [image_url],
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
                                        return {
                                            "status": "error",
                                            "message": f"Replicate API error: {error}"
                                        }
                        
                        return {
                            "status": "error",
                            "message": "Replicate API timeout - generation took too long"
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

