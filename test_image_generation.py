#!/usr/bin/env python3
"""Ð¢ÐµÑÑÐ¾Ð²ÑÐ¹ ÑÐºÑÐÐ¿Ñ Ð´Ð»Ñ Ð¿ÑÐ¾Ð²ÐµÑÐºÐ ÐÐµÐ½ÐµÑÐ°ÑÐÐ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐ¹ ÑÐµÑÐµÐ· OpenAI"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.image_generation_service import image_generation_service
from config import settings

async def test_generation():
    """Ð¢ÐµÑÑ ÐÐµÐ½ÐµÑÐ°ÑÐÐ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ"""
    print("=" * 60)
    print("Ð¢ÐµÑÑ ÐÐµÐ½ÐµÑÐ°ÑÐÐ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐ¹ ÑÐµÑÐµÐ· OpenAI")
    print("=" * 60)
    
    # ÐÑÐ¾Ð²ÐµÑÐºÐ° Ð½Ð°ÑÑÑÐ¾ÐµÐº
    print(f"\nÐÑÐ¾Ð²ÐµÑÐºÐ° Ð½Ð°ÑÑÑÐ¾ÐµÐº:")
    print(f"  OPENAI_API_KEY: {'Ð£ÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½' if settings.OPENAI_API_KEY else 'ÐÐ Ð£ÐÐ¢ÐÐÐÐÐÐÐ'}")
    if settings.OPENAI_API_KEY:
        print(f"  ÐÐ»ÑÑ Ð½Ð°ÑÐÐ½Ð°ÐµÑÑÑ Ñ: {settings.OPENAI_API_KEY[:20]}...")
    print(f"  IMAGE_GENERATION_PROVIDER: {settings.IMAGE_GENERATION_PROVIDER}")
    print(f"  ÐÑÐ¾Ð²Ð°Ð¹Ð´ÐµÑ Ð² ÑÐµÑÐ²ÐÑÐµ: {image_generation_service.provider}")
    print(f"  OpenAI ÐºÐ»ÑÑ Ð² ÑÐµÑÐ²ÐÑÐµ: {'ÐÑÑÑ' if image_generation_service.openai_key else 'ÐÐÐ¢'}")
    
    if not settings.OPENAI_API_KEY:
        print("\n ÐÐÐÐÐÐ: OPENAI_API_KEY Ð½Ðµ ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½ Ð² .env ÑÐ°Ð¹Ð»Ðµ!")
        return
    
    if settings.IMAGE_GENERATION_PROVIDER != "openai":
        print(f"\n  ÐÐÐÐÐÐÐÐ: IMAGE_GENERATION_PROVIDER={settings.IMAGE_GENERATION_PROVIDER}, Ð´Ð¾Ð»Ð¶ÐµÐ½ ÐÑÑÑ 'openai'")
    
    # Ð¢ÐµÑÑÐ¾Ð²Ð°Ñ ÐÐµÐ½ÐµÑÐ°ÑÐÑ
    print(f"\n{'=' * 60}")
    print("ÐÐ°Ð¿ÑÑÐº ÐÐµÐ½ÐµÑÐ°ÑÐÐ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ...")
    print(f"{'=' * 60}")
    
    test_prompt = "A beautiful sunset over the ocean, realistic photo"
    
    print(f"\nÐÑÐ¾Ð¼Ð¿Ñ: {test_prompt}")
    print("ÐÐ¶ÐÐ´Ð°Ð¹ÑÐµ...\n")
    
    try:
        result = await image_generation_service.generate_image(
            prompt=test_prompt,
            model="dall-e-3",
            width=1024,
            height=1024
        )
        
        print(f"\nÐÐµÐ·ÑÐ»ÑÑÐ°Ñ:")
        print(f"  ÐÑÐ°ÑÑÑ: {result.get('status')}")
        print(f"  ÐÐ¾Ð¾ÐÑÐµÐ½ÐÐµ: {result.get('message')}")
        
        if result.get("status") == "success":
            images = result.get("images", [])
            if images:
                print(f"\n Ð£ÐÐÐÐ! ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐµ ÑÐÐµÐ½ÐµÑÐÑÐ¾Ð²Ð°Ð½Ð¾:")
                print(f"  URL: {images[0]}")
            else:
                print(f"\n  ÐÑÐ°ÑÑÑ ÑÑÐ¿ÐµÑ, Ð½Ð¾ Ð½ÐµÑ URL ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ")
        else:
            print(f"\n ÐÐÐÐÐÐ ÐÐµÐ½ÐµÑÐ°ÑÐÐ:")
            print(f"  {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n ÐÐÐÐÐ®ÐÐÐÐÐ Ð¿ÑÐ ÐÐµÐ½ÐµÑÐ°ÑÐÐ:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generation())

