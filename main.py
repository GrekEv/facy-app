"""Главный файл запуска приложения"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from bot import bot, dp
from handlers import main_router
from database import init_db
from config import settings

logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot):
    """Установить команды бота"""
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="balance", description="💰 Мой баланс"),
        BotCommand(command="help", description="ℹ️ Помощь"),
    ]
    await bot.set_my_commands(commands)


async def on_startup():
    """Действия при запуске бота"""
    logger.info("Starting bot...")
    
    # Инициализация базы данных
    await init_db()
    logger.info("Database initialized")
    
    # Установка команд бота
    await set_bot_commands(bot)
    logger.info("Bot commands set")
    
    logger.info("Bot started successfully!")


async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("Shutting down bot...")
    await bot.session.close()


async def main():
    """Главная функция"""
    # Подключаем роутеры
    dp.include_router(main_router)
    
    # Регистрируем обработчики запуска и остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Запускаем бота
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

