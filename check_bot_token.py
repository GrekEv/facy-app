#!/usr/bin/env python3
"""ÐÑÐ¾Ð²ÐµÑÐºÐ° ÑÐ¾ÐºÐµÐ½Ð° ÐÐ¾ÑÐ°"""
import asyncio
from aiogram import Bot
from config import settings

async def test_token():
    if not settings.BOT_TOKEN:
        print("ÐÑÐÐÐºÐ°: BOT_TOKEN Ð½Ðµ ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½ Ð² .env")
        return
    
    print(f"ÐÑÐ¾Ð²ÐµÑÐºÐ° ÑÐ¾ÐºÐµÐ½Ð°... (Ð´Ð»ÐÐ½Ð°: {len(settings.BOT_TOKEN)})")
    
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        me = await bot.get_me()
        print(f"ÐÐ¾Ñ ÑÐ°ÐÐ¾ÑÐ°ÐµÑ!")
        print(f"   Username: @{me.username}")
        print(f"   ÐÐ¼Ñ: {me.first_name}")
        print(f"   ID: {me.id}")
        return True
    except Exception as e:
        print(f"ÐÑÐÐÐºÐ° Ð°Ð²ÑÐ¾ÑÐÐ·Ð°ÑÐÐ: {e}")
        print("\nÐÐ¾Ð·Ð¼Ð¾Ð¶Ð½ÑÐµ Ð¿ÑÐÑÐÐ½Ñ:")
        print("   1. Ð¢Ð¾ÐºÐµÐ½ Ð½ÐµÐ²ÐµÑÐ½ÑÐ¹ ÐÐ»Ð ÐÑÐ» Ð¾ÑÐ¾Ð·Ð²Ð°Ð½")
        print("   2. ÐÐ¾Ñ ÐÑÐ» ÑÐ´Ð°Ð»ÐµÐ½ ÐÐ»Ð Ð·Ð°ÐÐ»Ð¾ÐºÐÑÐ¾Ð²Ð°Ð½")
        print("   3. ÐÑÐ¾ÐÐ»ÐµÐ¼Ñ Ñ Ð´Ð¾ÑÑÑÐ¿Ð¾Ð¼ Ðº Telegram API")
        print("\nÐÑÐ¾Ð²ÐµÑÑÑÐµ ÑÐ¾ÐºÐµÐ½ Ð² .env ÑÐ°Ð¹Ð»Ðµ")
        return False
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_token())

