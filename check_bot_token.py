#!/usr/bin/env python3
"""��ове�ка токена �ота"""
import asyncio
from aiogram import Bot
from config import settings

async def test_token():
    if not settings.BOT_TOKEN:
        print("Ош��ка: BOT_TOKEN не у�тановлен в .env")
        return
    
    print(f"��ове�ка токена... (дл�на: {len(settings.BOT_TOKEN)})")
    
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        me = await bot.get_me()
        print(f"Бот �а�отает!")
        print(f"   Username: @{me.username}")
        print(f"   Им�: {me.first_name}")
        print(f"   ID: {me.id}")
        return True
    except Exception as e:
        print(f"Ош��ка авто��зац��: {e}")
        print("\n�озможн�е п��ч�н�:")
        print("   1. Токен неве�н�й �л� ��л отозван")
        print("   2. Бот ��л удален �л� за�лок��ован")
        print("   3. ��о�лем� � до�тупом к Telegram API")
        print("\n��ове��те токен в .env файле")
        return False
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_token())

