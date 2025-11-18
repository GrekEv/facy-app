"""�е�в�� дл� �а�от� � DeepFace API"""
import aiohttp
import logging
import os
from typing import Optional, Dict, Any
from config import settings

logger = logging.getLogger(__name__)


class DeepFaceService:
    """�е�в�� дл� замен� л�ц в в�део"""
    
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
        Замен�т� л�цо в в�део
        
        Args:
            source_image_path: �ут� к ���одному �зо��ажен�� л�ца
            target_video_path: �ут� к целевому в�део
            output_path: �ут� дл� �о��анен�� �езул�тата
            
        Returns:
            �езул�тат о��а�отк�
        """
        try:
            if not self.api_key:
                logger.warning("DeepFace API key not configured, using mock response")
                # � mock �еж�ме �оздаем пу�той файл дл� те�т��ован��
                import os
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w') as f:
                    f.write("")  # �оздаем пу�той файл
                return {
                    "status": "success",
                    "message": "Mock: DeepFace processing completed",
                    "output_path": output_path,
                    "task_id": "mock_task_123"
                }
            
            # �еал�н�й зап�о� к API DeepFace
            async with aiohttp.ClientSession() as session:
                # �од�отавл�ваем файл� дл� отп�авк�
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
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 м�нут таймаут
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Е�л� API возв�а�ает URL в�део, �кач�ваем е�о
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
        ��ове��т� �тату� задач�
        
        Args:
            task_id: ID задач�
            
        Returns:
            �тату� задач�
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

