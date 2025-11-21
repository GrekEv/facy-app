"""ÐÐµÑÐ²ÐÑ Ð´Ð»Ñ ÑÐ´Ð°Ð»ÐµÐ½ÐÑ ÑÐ¾Ð½Ð° ÐÐ· ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐ¹"""
import logging
from typing import Optional, Dict, Any
from PIL import Image
import numpy as np
import io

logger = logging.getLogger(__name__)


class BackgroundRemovalService:
    """ÐÐµÑÐ²ÐÑ Ð´Ð»Ñ ÑÐ´Ð°Ð»ÐµÐ½ÐÑ ÐÐµÐ»Ð¾ÐÐ¾/Ð¿ÑÐ¾Ð·ÑÐ°ÑÐ½Ð¾ÐÐ¾ ÑÐ¾Ð½Ð° ÐÐ· ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐ¹"""
    
    @staticmethod
    def remove_white_background(
        image_bytes: bytes,
        threshold: int = 240
    ) -> bytes:
        """
        Ð£Ð´Ð°Ð»ÐÑÑ ÐÐµÐ»ÑÐ¹ ÑÐ¾Ð½ ÐÐ· ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ
        
        Args:
            image_bytes: ÐÐ°Ð¹ÑÑ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ
            threshold: ÐÐ¾ÑÐ¾Ð Ð´Ð»Ñ Ð¾Ð¿ÑÐµÐ´ÐµÐ»ÐµÐ½ÐÑ ÐÐµÐ»Ð¾ÐÐ¾ ÑÐ²ÐµÑÐ° (0-255)
            
        Returns:
            ÐÐ°Ð¹ÑÑ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ Ñ Ð¿ÑÐ¾Ð·ÑÐ°ÑÐ½ÑÐ¼ ÑÐ¾Ð½Ð¾Ð¼ (PNG)
        """
        try:
            # ÐÑÐºÑÑÐ²Ð°ÐµÐ¼ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐµ
            image = Image.open(io.BytesIO(image_bytes))
            
            # ÐÐ¾Ð½Ð²ÐµÑÑÐÑÑÐµÐ¼ Ð² RGBA ÐµÑÐ»Ð Ð½ÑÐ¶Ð½Ð¾
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # ÐÑÐµÐ¾ÐÑÐ°Ð·ÑÐµÐ¼ Ð² numpy array
            data = np.array(image)
            
            # ÐÐ°ÑÐ¾Ð´ÐÐ¼ ÐÐµÐ»ÑÐµ Ð¿ÐÐºÑÐµÐ»Ð (ÐÐ´Ðµ R, G, B Ð²ÑÐµ Ð²ÑÑÐµ Ð¿Ð¾ÑÐ¾ÐÐ°)
            # ÐÑÐ¿Ð¾Ð»ÑÐ·ÑÐµÐ¼ ÐÐ¾Ð»ÐµÐµ Ð¼ÑÐÐºÐÐ¹ Ð¿Ð¾ÑÐ¾Ð Ð´Ð»Ñ Ð»ÑÑÑÐµÐÐ¾ ÑÐµÐ·ÑÐ»ÑÑÐ°ÑÐ°
            white_mask = (
                (data[:, :, 0] > threshold) & 
                (data[:, :, 1] > threshold) & 
                (data[:, :, 2] > threshold)
            )
            
            # ÐÐµÐ»Ð°ÐµÐ¼ ÐÐµÐ»ÑÐµ Ð¿ÐÐºÑÐµÐ»Ð Ð¿ÑÐ¾Ð·ÑÐ°ÑÐ½ÑÐ¼Ð
            data[:, :, 3] = np.where(white_mask, 0, data[:, :, 3])
            
            # ÐÐ¾Ð·Ð´Ð°ÐµÐ¼ Ð½Ð¾Ð²Ð¾Ðµ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐµ
            result_image = Image.fromarray(data, 'RGBA')
            
            # ÐÐ¾ÑÑÐ°Ð½ÑÐµÐ¼ Ð² PNG Ñ Ð¿ÑÐ¾Ð·ÑÐ°ÑÐ½Ð¾ÑÑÑÑ
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
        Ð£Ð¼Ð½Ð¾Ðµ ÑÐ´Ð°Ð»ÐµÐ½ÐÐµ ÑÐ¾Ð½Ð°
        
        Args:
            image_bytes: ÐÐ°Ð¹ÑÑ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ
            method: ÐÐµÑÐ¾Ð´ ÑÐ´Ð°Ð»ÐµÐ½ÐÑ ("white" Ð´Ð»Ñ ÐÐµÐ»Ð¾ÐÐ¾ ÑÐ¾Ð½Ð°, "edges" Ð´Ð»Ñ ÐºÑÐ°ÐµÐ²)
            
        Returns:
            ÐÐ°Ð¹ÑÑ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ Ñ Ð¿ÑÐ¾Ð·ÑÐ°ÑÐ½ÑÐ¼ ÑÐ¾Ð½Ð¾Ð¼ (PNG)
        """
        if method == "white":
            return BackgroundRemovalService.remove_white_background(image_bytes)
        else:
            # ÐÐ»Ñ Ð´ÑÑÐÐÑ Ð¼ÐµÑÐ¾Ð´Ð¾Ð² Ð¼Ð¾Ð¶Ð½Ð¾ Ð´Ð¾ÐÐ°Ð²ÐÑÑ ÐÐ¾Ð»ÐµÐµ ÑÐ»Ð¾Ð¶Ð½ÑÑ Ð»Ð¾ÐÐÐºÑ
            return BackgroundRemovalService.remove_white_background(image_bytes)
    
    @staticmethod
    async def process_image(
        image_bytes: bytes,
        remove_background: bool = True,
        threshold: int = 240
    ) -> Dict[str, Any]:
        """
        ÐÐÑÐ°ÐÐ¾ÑÐ°ÑÑ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐµ Ñ ÑÐ´Ð°Ð»ÐµÐ½ÐÐµÐ¼ ÑÐ¾Ð½Ð°
        
        Args:
            image_bytes: ÐÐ°Ð¹ÑÑ ÐÑÑÐ¾Ð´Ð½Ð¾ÐÐ¾ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ
            remove_background: Ð£Ð´Ð°Ð»ÑÑÑ Ð»Ð ÑÐ¾Ð½
            threshold: ÐÐ¾ÑÐ¾Ð Ð´Ð»Ñ Ð¾Ð¿ÑÐµÐ´ÐµÐ»ÐµÐ½ÐÑ ÐÐµÐ»Ð¾ÐÐ¾ ÑÐ²ÐµÑÐ°
            
        Returns:
            ÐÐ»Ð¾Ð²Ð°ÑÑ Ñ ÑÐµÐ·ÑÐ»ÑÑÐ°ÑÐ¾Ð¼ Ð¾ÐÑÐ°ÐÐ¾ÑÐºÐ
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

