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
    try:
        commands = [
            BotCommand(command="start", description="�лавное мен�"),
            BotCommand(command="balance", description="�ой �алан�"),
            BotCommand(command="help", description="�омо��"),
        ]
        await bot.set_my_commands(commands)
        logger.info("Bot commands set successfully")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")
        logger.warning("Bot will continue without custom commands")
async def on_startup():
    logger.info("Starting bot...")
    if not settings.BOT_TOKEN:
        logger.error("BOT_TOKEN not set! Please set BOT_TOKEN in .env file")
        raise ValueError("BOT_TOKEN is required")
    try:
        me = await bot.get_me()
        logger.info(f"Bot authorized: @{me.username} ({me.first_name})")
    except Exception as e:
        logger.error(f"Bot authorization failed: {e}")
        logger.error("Please check your BOT_TOKEN in .env file")
        logger.error("Get a new token from @BotFather in Telegram")
        raise
    await init_db()
    logger.info("Database initialized")
    await set_bot_commands(bot)
    logger.info("Bot started successfully!")
async def on_shutdown():
    logger.info("Shutting down bot...")
    await bot.session.close()
async def main():
    dp.include_router(main_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
