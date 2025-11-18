#!/usr/bin/env python3
"""–¢–µ——Ç–æ–≤—–π —–∫—––ø—Ç –¥–ª— –ø—–æ–≤–µ—–∫– ––µ–Ω–µ—–∞—Ü–– ––∑–æ–—–∞–∂–µ–Ω––π —á–µ—–µ–∑ OpenAI"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.image_generation_service import image_generation_service
from config import settings

async def test_generation():
    """–¢–µ——Ç ––µ–Ω–µ—–∞—Ü–– ––∑–æ–—–∞–∂–µ–Ω–—"""
    print("=" * 60)
    print("–¢–µ——Ç ––µ–Ω–µ—–∞—Ü–– ––∑–æ–—–∞–∂–µ–Ω––π —á–µ—–µ–∑ OpenAI")
    print("=" * 60)
    
    # –—–æ–≤–µ—–∫–∞ –Ω–∞——Ç—–æ–µ–∫
    print(f"\n–—–æ–≤–µ—–∫–∞ –Ω–∞——Ç—–æ–µ–∫:")
    print(f"  OPENAI_API_KEY: {'–£——Ç–∞–Ω–æ–≤–ª–µ–Ω' if settings.OPENAI_API_KEY else '––ï –£––¢–––û––õ–ï–'}")
    if settings.OPENAI_API_KEY:
        print(f"  ––ª——á –Ω–∞—á––Ω–∞–µ—Ç—— —: {settings.OPENAI_API_KEY[:20]}...")
    print(f"  IMAGE_GENERATION_PROVIDER: {settings.IMAGE_GENERATION_PROVIDER}")
    print(f"  –—–æ–≤–∞–π–¥–µ— –≤ —–µ—–≤–—–µ: {image_generation_service.provider}")
    print(f"  OpenAI –∫–ª——á –≤ —–µ—–≤–—–µ: {'–ï——Ç—' if image_generation_service.openai_key else '––ï–¢'}")
    
    if not settings.OPENAI_API_KEY:
        print("\n –û––ò–ë––: OPENAI_API_KEY –Ω–µ —É——Ç–∞–Ω–æ–≤–ª–µ–Ω –≤ .env —Ñ–∞–π–ª–µ!")
        return
    
    if settings.IMAGE_GENERATION_PROVIDER != "openai":
        print(f"\n  –––ò––––ò–ï: IMAGE_GENERATION_PROVIDER={settings.IMAGE_GENERATION_PROVIDER}, –¥–æ–ª–∂–µ–Ω –——Ç— 'openai'")
    
    # –¢–µ——Ç–æ–≤–∞— ––µ–Ω–µ—–∞—Ü–—
    print(f"\n{'=' * 60}")
    print("–ó–∞–ø—É—–∫ ––µ–Ω–µ—–∞—Ü–– ––∑–æ–—–∞–∂–µ–Ω–—...")
    print(f"{'=' * 60}")
    
    test_prompt = "A beautiful sunset over the ocean, realistic photo"
    
    print(f"\n–—–æ–º–ø—Ç: {test_prompt}")
    print("–û–∂––¥–∞–π—Ç–µ...\n")
    
    try:
        result = await image_generation_service.generate_image(
            prompt=test_prompt,
            model="dall-e-3",
            width=1024,
            height=1024
        )
        
        print(f"\n––µ–∑—É–ª——Ç–∞—Ç:")
        print(f"  –—Ç–∞—Ç—É—: {result.get('status')}")
        print(f"  ––æ–æ–—–µ–Ω––µ: {result.get('message')}")
        
        if result.get("status") == "success":
            images = result.get("images", [])
            if images:
                print(f"\n –£–––ï–! –ò–∑–æ–—–∞–∂–µ–Ω––µ —––µ–Ω–µ—–—–æ–≤–∞–Ω–æ:")
                print(f"  URL: {images[0]}")
            else:
                print(f"\n  –—Ç–∞—Ç—É— —É—–ø–µ—, –Ω–æ –Ω–µ—Ç URL ––∑–æ–—–∞–∂–µ–Ω–—")
        else:
            print(f"\n –û––ò–ë–– ––µ–Ω–µ—–∞—Ü––:")
            print(f"  {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n –ò–––õ–Æ––ï––ò–ï –ø—– ––µ–Ω–µ—–∞—Ü––:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generation())

