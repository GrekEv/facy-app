"""�е�в�� дл� удален�� фона �з �зо��ажен�й"""
import logging
from typing import Optional, Dict, Any
from PIL import Image
import numpy as np
import io

logger = logging.getLogger(__name__)


class BackgroundRemovalService:
    """�е�в�� дл� удален�� �ело�о/п�оз�ачно�о фона �з �зо��ажен�й"""
    
    @staticmethod
    def remove_white_background(
        image_bytes: bytes,
        threshold: int = 240
    ) -> bytes:
        """
        Удал�т� �ел�й фон �з �зо��ажен��
        
        Args:
            image_bytes: Байт� �зо��ажен��
            threshold: �о�о� дл� оп�еделен�� �ело�о цвета (0-255)
            
        Returns:
            Байт� �зо��ажен�� � п�оз�ачн�м фоном (PNG)
        """
        try:
            # Отк��ваем �зо��ажен�е
            image = Image.open(io.BytesIO(image_bytes))
            
            # �онве�т��уем в RGBA е�л� нужно
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # ��ео��азуем в numpy array
            data = np.array(image)
            
            # �а�од�м �ел�е п�к�ел� (�де R, G, B в�е в�ше по�о�а)
            # И�пол�зуем �олее м��к�й по�о� дл� лучше�о �езул�тата
            white_mask = (
                (data[:, :, 0] > threshold) & 
                (data[:, :, 1] > threshold) & 
                (data[:, :, 2] > threshold)
            )
            
            # �елаем �ел�е п�к�ел� п�оз�ачн�м�
            data[:, :, 3] = np.where(white_mask, 0, data[:, :, 3])
            
            # �оздаем новое �зо��ажен�е
            result_image = Image.fromarray(data, 'RGBA')
            
            # �о��ан�ем в PNG � п�оз�ачно�т��
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
        Умное удален�е фона
        
        Args:
            image_bytes: Байт� �зо��ажен��
            method: �етод удален�� ("white" дл� �ело�о фона, "edges" дл� к�аев)
            
        Returns:
            Байт� �зо��ажен�� � п�оз�ачн�м фоном (PNG)
        """
        if method == "white":
            return BackgroundRemovalService.remove_white_background(image_bytes)
        else:
            # �л� д�у��� методов можно до�ав�т� �олее �ложну� ло��ку
            return BackgroundRemovalService.remove_white_background(image_bytes)
    
    @staticmethod
    async def process_image(
        image_bytes: bytes,
        remove_background: bool = True,
        threshold: int = 240
    ) -> Dict[str, Any]:
        """
        О��а�отат� �зо��ажен�е � удален�ем фона
        
        Args:
            image_bytes: Байт� ���одно�о �зо��ажен��
            remove_background: Удал�т� л� фон
            threshold: �о�о� дл� оп�еделен�� �ело�о цвета
            
        Returns:
            �лова�� � �езул�татом о��а�отк�
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

