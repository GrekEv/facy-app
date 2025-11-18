"""Сервис для удаления фона из изображений"""
import logging
from typing import Optional, Dict, Any
from PIL import Image
import numpy as np
import io

logger = logging.getLogger(__name__)


class BackgroundRemovalService:
    """Сервис для удаления белого/прозрачного фона из изображений"""
    
    @staticmethod
    def remove_white_background(
        image_bytes: bytes,
        threshold: int = 240
    ) -> bytes:
        """
        Удалить белый фон из изображения
        
        Args:
            image_bytes: Байты изображения
            threshold: Порог для определения белого цвета (0-255)
            
        Returns:
            Байты изображения с прозрачным фоном (PNG)
        """
        try:
            # Открываем изображение
            image = Image.open(io.BytesIO(image_bytes))
            
            # Конвертируем в RGBA если нужно
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Преобразуем в numpy array
            data = np.array(image)
            
            # Находим белые пиксели (где R, G, B все выше порога)
            # Используем более мягкий порог для лучшего результата
            white_mask = (
                (data[:, :, 0] > threshold) & 
                (data[:, :, 1] > threshold) & 
                (data[:, :, 2] > threshold)
            )
            
            # Делаем белые пиксели прозрачными
            data[:, :, 3] = np.where(white_mask, 0, data[:, :, 3])
            
            # Создаем новое изображение
            result_image = Image.fromarray(data, 'RGBA')
            
            # Сохраняем в PNG с прозрачностью
            output = io.BytesIO()
            result_image.save(output, format='PNG', optimize=True)
            output.seek(0)
            
            logger.info(f"Background removed successfully, size: {len(output.getvalue())} bytes")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error removing background: {e}")
            raise
    
    @staticmethod
    def remove_background_smart(
        image_bytes: bytes,
        method: str = "white"
    ) -> bytes:
        """
        Умное удаление фона
        
        Args:
            image_bytes: Байты изображения
            method: Метод удаления ("white" для белого фона, "edges" для краев)
            
        Returns:
            Байты изображения с прозрачным фоном (PNG)
        """
        if method == "white":
            return BackgroundRemovalService.remove_white_background(image_bytes)
        else:
            # Для других методов можно добавить более сложную логику
            return BackgroundRemovalService.remove_white_background(image_bytes)
    
    @staticmethod
    async def process_image(
        image_bytes: bytes,
        remove_background: bool = True,
        threshold: int = 240
    ) -> Dict[str, Any]:
        """
        Обработать изображение с удалением фона
        
        Args:
            image_bytes: Байты исходного изображения
            remove_background: Удалять ли фон
            threshold: Порог для определения белого цвета
            
        Returns:
            Словарь с результатом обработки
        """
        try:
            if not remove_background:
                return {
                    "status": "success",
                    "image_bytes": image_bytes,
                    "format": "original"
                }
            
            processed_bytes = BackgroundRemovalService.remove_white_background(
                image_bytes,
                threshold
            )
            
            return {
                "status": "success",
                "image_bytes": processed_bytes,
                "format": "PNG"
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


background_removal_service = BackgroundRemovalService()

