#!/usr/bin/env python3
"""Тестовый скрипт для проверки генерации изображений через OpenAI"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.image_generation_service import image_generation_service
from config import settings

async def test_generation():
    """Тест генерации изображения"""
    print("=" * 60)
    print("Тест генерации изображений через OpenAI")
    print("=" * 60)
    
    # Проверка настроек
    print(f"\nПроверка настроек:")
    print(f"  OPENAI_API_KEY: {'Установлен' if settings.OPENAI_API_KEY else 'НЕ УСТАНОВЛЕН'}")
    if settings.OPENAI_API_KEY:
        print(f"  Ключ начинается с: {settings.OPENAI_API_KEY[:20]}...")
    print(f"  IMAGE_GENERATION_PROVIDER: {settings.IMAGE_GENERATION_PROVIDER}")
    print(f"  Провайдер в сервисе: {image_generation_service.provider}")
    print(f"  OpenAI ключ в сервисе: {'Есть' if image_generation_service.openai_key else 'НЕТ'}")
    
    if not settings.OPENAI_API_KEY:
        print("\n❌ ОШИБКА: OPENAI_API_KEY не установлен в .env файле!")
        return
    
    if settings.IMAGE_GENERATION_PROVIDER != "openai":
        print(f"\n⚠️  ВНИМАНИЕ: IMAGE_GENERATION_PROVIDER={settings.IMAGE_GENERATION_PROVIDER}, должен быть 'openai'")
    
    # Тестовая генерация
    print(f"\n{'=' * 60}")
    print("Запуск генерации изображения...")
    print(f"{'=' * 60}")
    
    test_prompt = "A beautiful sunset over the ocean, realistic photo"
    
    print(f"\nПромпт: {test_prompt}")
    print("Ожидайте...\n")
    
    try:
        result = await image_generation_service.generate_image(
            prompt=test_prompt,
            model="dall-e-3",
            width=1024,
            height=1024
        )
        
        print(f"\nРезультат:")
        print(f"  Статус: {result.get('status')}")
        print(f"  Сообщение: {result.get('message')}")
        
        if result.get("status") == "success":
            images = result.get("images", [])
            if images:
                print(f"\n✅ УСПЕХ! Изображение сгенерировано:")
                print(f"  URL: {images[0]}")
            else:
                print(f"\n⚠️  Статус успех, но нет URL изображения")
        else:
            print(f"\n❌ ОШИБКА генерации:")
            print(f"  {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ ИСКЛЮЧЕНИЕ при генерации:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_generation())

