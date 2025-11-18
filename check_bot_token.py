#!/usr/bin/env python3
"""Проверка токена бота"""
import asyncio
from aiogram import Bot
from config import settings

async def test_token():
    if not settings.BOT_TOKEN:
        print("❌ BOT_TOKEN не установлен в .env")
        return
    
    print(f"🔍 Проверка токена... (длина: {len(settings.BOT_TOKEN)})")
    
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        me = await bot.get_me()
        print(f"✅ Бот работает!")
        print(f"   Username: @{me.username}")
        print(f"   Имя: {me.first_name}")
        print(f"   ID: {me.id}")
        return True
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        print("\n💡 Возможные причины:")
        print("   1. Токен неверный или был отозван")
        print("   2. Бот был удален или заблокирован")
        print("   3. Проблемы с доступом к Telegram API")
        print("\n📝 Проверьте токен в .env файле")
        return False
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_token())

