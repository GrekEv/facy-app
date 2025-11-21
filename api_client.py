#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
�л�ент�к�й �к��пт дл� �а�от� � API п��ложен��
�озвол�ет �ене���оват� �зо��ажен�� � в�део, получат� �езул�тат�
"""
import asyncio
import aiohttp
import argparse
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json

# Цвета дл� в�вода
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color


class APIClient:
    """�л�ент дл� �а�от� � API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Ин�ц�ал�зац�� кл�ента
        
        Args:
            base_url: Базов�й URL API �е�ве�а
        """
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """���н��онн�й контек�тн�й менедже� - в�од"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """���н��онн�й контек�тн�й менедже� - в��од"""
        if self.session:
            await self.session.close()
    
    def _print_success(self, message: str):
        """��ве�т� �оо��ен�е о� у�пе�е"""
        print(f"{GREEN}[OK] {message}{NC}")
    
    def _print_error(self, message: str):
        """��ве�т� �оо��ен�е о� ош��ке"""
        print(f"{RED}[ERROR] {message}{NC}")
    
    def _print_info(self, message: str):
        """��ве�т� �нфо�мац�онное �оо��ен�е"""
        print(f"{BLUE}[INFO] {message}{NC}")
    
    def _print_warning(self, message: str):
        """��ве�т� п�едуп�ежден�е"""
        print(f"{YELLOW}[WARN] {message}{NC}")
    
    async def generate_image(
        self,
        telegram_id: int,
        prompt: str,
        model: str = "flux",
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, Any]:
        """
        �ене���оват� �зо��ажен�е
        
        Args:
            telegram_id: ID пол�зовател� Telegram
            prompt: Тек�товое оп��ан�е �зо��ажен��
            model: �одел� дл� �ене�ац��
            style: �т�л� �зо��ажен��
            negative_prompt: �е�ат�вн�й п�омпт
            width: ����на �зо��ажен��
            height: ���ота �зо��ажен��
            
        Returns:
            �езул�тат �ене�ац��
        """
        self._print_info(f"�ене�ац�� �зо��ажен��: {prompt[:50]}...")
        
        url = f"{self.base_url}/api/generate/image"
        payload = {
            "telegram_id": telegram_id,
            "prompt": prompt,
            "model": model,
            "width": width,
            "height": height
        }
        
        if style:
            payload["style"] = style
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        self._print_success(f"Изо��ажен�е ��ене���овано!")
                        self._print_info(f"URL: {result.get('image_url')}")
                        return result
                    else:
                        self._print_error(f"Ош��ка: {result.get('message', 'Unknown error')}")
                        return result
                else:
                    error_text = await response.text()
                    self._print_error(f"HTTP {response.status}: {error_text}")
                    return {"success": False, "message": error_text}
        except Exception as e:
            self._print_error(f"Ош��ка зап�о�а: {e}")
            return {"success": False, "message": str(e)}
    
    async def generate_video(
        self,
        telegram_id: int,
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
        �ене���оват� в�део
        
        Args:
            telegram_id: ID пол�зовател� Telegram
            prompt: Тек�товое оп��ан�е в�део
            model: �одел� дл� �ене�ац��
            style: �т�л� в�део
            negative_prompt: �е�ат�вн�й п�омпт
            duration: �л�тел�но�т� в �екунда�
            fps: �ад�ов в �екунду
            width: ����на в�део
            height: ���ота в�део
            
        Returns:
            �езул�тат �ене�ац��
        """
        self._print_info(f"�ене�ац�� в�део: {prompt[:50]}...")
        
        url = f"{self.base_url}/api/generate/video"
        payload = {
            "telegram_id": telegram_id,
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "fps": fps,
            "width": width,
            "height": height
        }
        
        if style:
            payload["style"] = style
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        self._print_success(f"�ене�ац�� в�део запу�ена!")
                        if result.get("video_url"):
                            self._print_info(f"URL: {result.get('video_url')}")
                        if result.get("task_id"):
                            self._print_info(f"Task ID: {result.get('task_id')}")
                        return result
                    else:
                        self._print_error(f"Ош��ка: {result.get('message', 'Unknown error')}")
                        return result
                else:
                    error_text = await response.text()
                    self._print_error(f"HTTP {response.status}: {error_text}")
                    return {"success": False, "message": error_text}
        except Exception as e:
            self._print_error(f"Ош��ка зап�о�а: {e}")
            return {"success": False, "message": str(e)}
    
    async def check_video_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        ��ове��т� �тату� задач� �ене�ац�� в�део
        
        Args:
            task_id: ID задач�
            
        Returns:
            �тату� задач�
        """
        url = f"{self.base_url}/api/video/task/{task_id}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    status = result.get("status", "unknown")
                    progress = result.get("progress", 0)
                    
                    if status == "completed":
                        self._print_success(f"��део �отово! ��о��е��: {progress}%")
                        if result.get("video_url"):
                            self._print_info(f"URL: {result.get('video_url')}")
                    elif status == "processing":
                        self._print_info(f"О��а�отка... ��о��е��: {progress}%")
                    elif status == "failed":
                        self._print_error(f"Ош��ка: {result.get('message', 'Unknown error')}")
                    else:
                        self._print_warning(f"�тату�: {status}")
                    
                    return result
                else:
                    error_text = await response.text()
                    self._print_error(f"HTTP {response.status}: {error_text}")
                    return {"status": "error", "message": error_text}
        except Exception as e:
            self._print_error(f"Ош��ка зап�о�а: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_user_info(self, telegram_id: int) -> Dict[str, Any]:
        """
        �олуч�т� �нфо�мац�� о пол�зователе
        
        Args:
            telegram_id: ID пол�зовател� Telegram
            
        Returns:
            Инфо�мац�� о пол�зователе
        """
        url = f"{self.base_url}/api/user/{telegram_id}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    self._print_success("Инфо�мац�� о пол�зователе получена")
                    return result
                else:
                    error_text = await response.text()
                    self._print_error(f"HTTP {response.status}: {error_text}")
                    return {}
        except Exception as e:
            self._print_error(f"Ош��ка зап�о�а: {e}")
            return {}
    
    async def get_models(self) -> Dict[str, Any]:
        """�олуч�т� �п��ок до�тупн�� моделей дл� �зо��ажен�й"""
        url = f"{self.base_url}/api/models"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return {"models": []}
        except Exception as e:
            self._print_error(f"Ош��ка зап�о�а: {e}")
            return {"models": []}
    
    async def get_video_models(self) -> Dict[str, Any]:
        """�олуч�т� �п��ок до�тупн�� моделей дл� в�део"""
        url = f"{self.base_url}/api/video/models"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return {"models": []}
        except Exception as e:
            self._print_error(f"Ош��ка зап�о�а: {e}")
            return {"models": []}
    
    async def download_file(self, url: str, output_path: Path) -> bool:
        """
        �качат� файл по URL
        
        Args:
            url: URL файла (может ��т� отно��тел�н�м �л� а��ол�тн�м)
            output_path: �ут� дл� �о��анен�� файла
            
        Returns:
            True е�л� у�пешно
        """
        # Е�л� URL отно��тел�н�й, до�авл�ем �азов�й URL
        if url.startswith('/'):
            url = f"{self.base_url}{url}"
        
        self._print_info(f"�кач�ван�е файла: {url}")
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    # �оздаем д��екто��� е�л� нужно
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # �о��ан�ем файл
                    with open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    
                    self._print_success(f"Файл �о��анен: {output_path}")
                    return True
                else:
                    self._print_error(f"HTTP {response.status}: �е удало�� �качат� файл")
                    return False
        except Exception as e:
            self._print_error(f"Ош��ка �кач�ван��: {e}")
            return False
    
    async def health_check(self) -> bool:
        """��ове��т� до�тупно�т� API"""
        url = f"{self.base_url}/health"
        
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "healthy":
                        self._print_success("API до�тупен")
                        return True
                    else:
                        self._print_warning(f"API ве�нул: {result}")
                        return False
                else:
                    self._print_error(f"HTTP {response.status}")
                    return False
        except asyncio.TimeoutError:
            self._print_error("Таймаут подкл�чен�� к API")
            return False
        except Exception as e:
            self._print_error(f"Ош��ка подкл�чен��: {e}")
            return False


async def main():
    """О�новна� функц��"""
    parser = argparse.ArgumentParser(
        description="�л�ент дл� �а�от� � API �ене�ац�� �зо��ажен�й � в�део",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
���ме�� ��пол�зован��:

  # �ене�ац�� �зо��ажен��
  python api_client.py image --telegram-id 123456789 --prompt "��а��в�й закат над мо�ем"

  # �ене�ац�� в�део
  python api_client.py video --telegram-id 123456789 --prompt "�от ���ает � м�чом"

  # ��ове�ка �тату�а в�део
  python api_client.py status --task-id task_123

  # �олучен�е �нфо�мац�� о пол�зователе
  python api_client.py user --telegram-id 123456789

  # �кач�ван�е файла
  python api_client.py download --url /generated/video.mp4 --output ./downloads/video.mp4

  # ��ове�ка до�тупно�т� API
  python api_client.py health
        """
    )
    
    parser.add_argument(
        '--base-url',
        default=os.getenv('API_BASE_URL', 'http://localhost:8000'),
        help='Базов�й URL API (по умолчан��: http://localhost:8000)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='�оманд�')
    
    # �оманда �ене�ац�� �зо��ажен��
    image_parser = subparsers.add_parser('image', help='�ене���оват� �зо��ажен�е')
    image_parser.add_argument('--telegram-id', type=int, required=True, help='ID пол�зовател� Telegram')
    image_parser.add_argument('--prompt', required=True, help='Тек�товое оп��ан�е �зо��ажен��')
    image_parser.add_argument('--model', default='flux', help='�одел� (по умолчан��: flux)')
    image_parser.add_argument('--style', help='�т�л� �зо��ажен��')
    image_parser.add_argument('--negative-prompt', help='�е�ат�вн�й п�омпт')
    image_parser.add_argument('--width', type=int, default=1024, help='����на (по умолчан��: 1024)')
    image_parser.add_argument('--height', type=int, default=1024, help='���ота (по умолчан��: 1024)')
    image_parser.add_argument('--download', action='store_true', help='�качат� �зо��ажен�е')
    image_parser.add_argument('--output', type=Path, default=Path('./downloads'), help='���екто��� дл� �о��анен��')
    
    # �оманда �ене�ац�� в�део
    video_parser = subparsers.add_parser('video', help='�ене���оват� в�део')
    video_parser.add_argument('--telegram-id', type=int, required=True, help='ID пол�зовател� Telegram')
    video_parser.add_argument('--prompt', required=True, help='Тек�товое оп��ан�е в�део')
    video_parser.add_argument('--model', default='runway', help='�одел� (по умолчан��: runway)')
    video_parser.add_argument('--style', help='�т�л� в�део')
    video_parser.add_argument('--negative-prompt', help='�е�ат�вн�й п�омпт')
    video_parser.add_argument('--duration', type=int, default=5, help='�л�тел�но�т� в �екунда� (по умолчан��: 5)')
    video_parser.add_argument('--fps', type=int, default=24, help='�ад�ов в �екунду (по умолчан��: 24)')
    video_parser.add_argument('--width', type=int, default=1280, help='����на (по умолчан��: 1280)')
    video_parser.add_argument('--height', type=int, default=720, help='���ота (по умолчан��: 720)')
    
    # �оманда п�ове�к� �тату�а
    status_parser = subparsers.add_parser('status', help='��ове��т� �тату� задач� �ене�ац�� в�део')
    status_parser.add_argument('--task-id', required=True, help='ID задач�')
    
    # �оманда получен�� �нфо�мац�� о пол�зователе
    user_parser = subparsers.add_parser('user', help='�олуч�т� �нфо�мац�� о пол�зователе')
    user_parser.add_argument('--telegram-id', type=int, required=True, help='ID пол�зовател� Telegram')
    
    # �оманда �кач�ван�� файла
    download_parser = subparsers.add_parser('download', help='�качат� файл')
    download_parser.add_argument('--url', required=True, help='URL файла (может ��т� отно��тел�н�м)')
    download_parser.add_argument('--output', type=Path, required=True, help='�ут� дл� �о��анен�� файла')
    
    # �оманда п�ове�к� здо�ов��
    subparsers.add_parser('health', help='��ове��т� до�тупно�т� API')
    
    # �оманда �п��ка моделей
    models_parser = subparsers.add_parser('models', help='�олуч�т� �п��ок моделей')
    models_parser.add_argument('--type', choices=['image', 'video'], default='image', help='Т�п моделей')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    async with APIClient(base_url=args.base_url) as client:
        if args.command == 'health':
            await client.health_check()
        
        elif args.command == 'image':
            result = await client.generate_image(
                telegram_id=args.telegram_id,
                prompt=args.prompt,
                model=args.model,
                style=args.style,
                negative_prompt=args.negative_prompt,
                width=args.width,
                height=args.height
            )
            
            if result.get("success") and args.download:
                image_url = result.get("image_url")
                if image_url:
                    # Оп�едел�ем �м� файла
                    filename = image_url.split('/')[-1]
                    if not filename or '.' not in filename:
                        filename = f"image_{result.get('generation_id', 'unknown')}.png"
                    
                    output_path = args.output / filename
                    await client.download_file(image_url, output_path)
        
        elif args.command == 'video':
            result = await client.generate_video(
                telegram_id=args.telegram_id,
                prompt=args.prompt,
                model=args.model,
                style=args.style,
                negative_prompt=args.negative_prompt,
                duration=args.duration,
                fps=args.fps,
                width=args.width,
                height=args.height
            )
            
            if result.get("success"):
                print(f"\n{CYAN}�л� п�ове�к� �тату�а ��пол�зуйте:{NC}")
                print(f"python api_client.py status --task-id {result.get('task_id')}")
        
        elif args.command == 'status':
            await client.check_video_task_status(args.task_id)
        
        elif args.command == 'user':
            result = await client.get_user_info(args.telegram_id)
            if result:
                print(f"\n{CYAN}Инфо�мац�� о пол�зователе:{NC}")
                print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.command == 'download':
            await client.download_file(args.url, args.output)
        
        elif args.command == 'models':
            if args.type == 'image':
                result = await client.get_models()
            else:
                result = await client.get_video_models()
            
            if result.get("models"):
                print(f"\n{CYAN}�о�тупн�е модел� ({args.type}):{NC}")
                for model in result["models"]:
                    if isinstance(model, dict):
                        print(f"  - {model.get('id', model.get('name', 'Unknown'))}: {model.get('description', '')}")
                    else:
                        print(f"  - {model}")
            else:
                print(f"{YELLOW}�одел� не найден�{NC}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}��е�вано пол�зователем{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}���т�че�ка� ош��ка: {e}{NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


