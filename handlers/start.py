from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import settings
import logging
logger = logging.getLogger(__name__)
router = Router()
def get_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    webapp_url = settings.webapp_url
    builder.row(
        InlineKeyboardButton(
            text="РћС‚РєССС‚С РїСРР»РѕР¶РµРЅРРµ",
            web_app=WebAppInfo(url=webapp_url)
        )
    )
    builder.row(
        InlineKeyboardButton(text="РРѕР№ РР°Р»Р°РЅС", callback_data="balance"),
        InlineKeyboardButton(text="РС‚Р°С‚РСС‚РРєР°", callback_data="stats")
    )
    builder.row(
        InlineKeyboardButton(text="РСѓРїРС‚С РїРѕРРЅС‚С", callback_data="buy_points"),
    )
    builder.row(
        InlineKeyboardButton(text="РРѕРјРѕСС", callback_data="help")
    )
    return builder.as_markup()
@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    referral_code = None
    if message.text and len(message.text.split()) > 1:
        referral_code = message.text.split()[1]
        logger.info(f"User {user.id} started with referral code: {referral_code}")
        try:
            from database import get_session
            from services.user_service import UserService
            from sqlalchemy.ext.asyncio import AsyncSession
            from sqlalchemy import select
            from database.models import User
            async for session in get_session():
                ref_result = await session.execute(
                    select(User).where(User.referral_code == referral_code)
                )
                referrer = ref_result.scalar_one_or_none()
                if referrer:
                    new_user = await UserService.create_user_with_referral(
                        session=session,
                        telegram_id=user.id,
                        username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        language_code=user.language_code or "ru",
                        referral_code=referral_code
                    )
                    logger.info(f"User {user.id} registered with referral from {referrer.telegram_id}")
                else:
                    logger.warning(f"Referral code {referral_code} not found")
                    await UserService.create_user_with_referral(
                        session=session,
                        telegram_id=user.id,
                        username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        language_code=user.language_code or "ru",
                        referral_code=None
                    )
                break
        except Exception as e:
            logger.error(f"Error processing referral code: {e}")
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback):
    await callback.message.edit_text(
        "<b>РР»Р°РІРЅРѕРµ РјРµРЅС</b>\n\nРСРРµСРС‚Рµ РґРµР№СС‚РІРРµ:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()
