from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Generation
from datetime import datetime, timedelta
from typing import Optional
import logging
import secrets
import string
logger = logging.getLogger(__name__)
class UserService:
    @staticmethod
    async def get_or_create_user(
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "ru"
    ) -> User:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.last_active = datetime.utcnow()
            if not user.referral_code:
                new_referral_code = UserService.generate_referral_code()
                while True:
                    check_result = await session.execute(
                        select(User).where(User.referral_code == new_referral_code)
                    )
                    if check_result.scalar_one_or_none() is None:
                        break
                    new_referral_code = UserService.generate_referral_code()
                user.referral_code = new_referral_code
                await session.commit()
                await session.refresh(user)
                logger.info(f"Generated referral_code {new_referral_code} for existing user {telegram_id}")
            else:
                await session.commit()
            return user
        new_referral_code = UserService.generate_referral_code()
        while True:
            check_result = await session.execute(
                select(User).where(User.referral_code == new_referral_code)
            )
            if check_result.scalar_one_or_none() is None:
                break
            new_referral_code = UserService.generate_referral_code()
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            referral_code=new_referral_code
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"Created new user: {telegram_id} with referral_code: {new_referral_code}")
        return user
    @staticmethod
    async def get_user_by_id(
        session: AsyncSession,
        user_id: int
    ) -> Optional[User]:
        return await session.get(User, user_id)
    @staticmethod
    async def get_user_by_telegram_id(
        session: AsyncSession,
        telegram_id: int
    ) -> Optional[User]:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    @staticmethod
    async def update_balance(
        session: AsyncSession,
        user: User,
        amount: int
    ) -> bool:
        new_balance = user.balance + amount
        if new_balance < 0:
            logger.warning(f"Insufficient balance for user {user.telegram_id}")
            return False
        user.balance = new_balance
        await session.commit()
        logger.info(f"Updated balance for user {user.telegram_id}: {amount} (new: {new_balance})")
        return True
    @staticmethod
    async def can_afford(user: User, cost: int) -> bool:
        return user.balance >= cost or user.free_generations > 0
    @staticmethod
    def generate_referral_code() -> str:
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(8))
    @staticmethod
    def generate_verification_code() -> str:
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    @staticmethod
    async def send_verification_code(
        session: AsyncSession,
        telegram_id: int,
        email: str
    ) -> tuple[bool, Optional[str]]:
        from services.email_service import EmailService
        if not EmailService.validate_email(email):
            return False, "Неверный формат email"
        user = await UserService.get_or_create_user(
            session,
            telegram_id=telegram_id
        )
        code = UserService.generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        user.email = email.lower().strip()
        user.verification_code = code
        user.verification_code_expires = expires_at
        user.email_verified = False
        await session.commit()
        success = await EmailService.send_verification_code(email, code)
        if success:
            logger.info(f"Verification code sent to {email} for user {telegram_id}")
            return True, None
        else:
            logger.error(f"Failed to send verification code to {email}")
            return False, "Не удалось отправить код. Проверьте настройки SMTP."
    @staticmethod
    async def verify_email_code(
        session: AsyncSession,
        telegram_id: int,
        code: str
    ) -> tuple[bool, Optional[str]]:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False, "Пользователь не найден"
        if not user.verification_code:
            return False, "Код подтверждения не был отправлен"
        if user.verification_code != code:
            return False, "Неверный код подтверждения"
        if user.verification_code_expires and user.verification_code_expires < datetime.utcnow():
            return False, "Код подтверждения истек. Запросите новый код."
        user.email_verified = True
        user.verification_code = None
        user.verification_code_expires = None
        await session.commit()
        logger.info(f"Email verified for user {telegram_id}: {user.email}")
        return True, None
    @staticmethod
    async def create_user_with_referral(
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "ru",
        referral_code: Optional[str] = None
    ) -> User:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            existing_user.last_active = datetime.utcnow()
            await session.commit()
            return existing_user
        referred_by_id = None
        if referral_code:
            ref_result = await session.execute(
                select(User).where(User.referral_code == referral_code)
            )
            referrer = ref_result.scalar_one_or_none()
            if referrer:
                referred_by_id = referrer.id
                referrer.referral_balance += 10.0
                logger.info(f"User {referrer.telegram_id} referred new user {telegram_id}")
            else:
                logger.warning(f"Referral code {referral_code} not found in database")
        new_referral_code = UserService.generate_referral_code()
        while True:
            check_result = await session.execute(
                select(User).where(User.referral_code == new_referral_code)
            )
            if check_result.scalar_one_or_none() is None:
                break
            new_referral_code = UserService.generate_referral_code()
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            referral_code=new_referral_code,
            referred_by=referred_by_id
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"Created new user: {telegram_id} with referral_code: {new_referral_code}")
        return user
    @staticmethod
    async def get_stats(session: AsyncSession) -> dict:
        total_users_result = await session.execute(
            select(func.count(User.id))
        )
        total_users = total_users_result.scalar() or 0
        total_generations_result = await session.execute(
            select(func.sum(User.total_generations))
        )
        total_generations = total_generations_result.scalar() or 0
        total_deepfakes_result = await session.execute(
            select(func.sum(User.total_deepfakes))
        )
        total_deepfakes = total_deepfakes_result.scalar() or 0
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        active_users_result = await session.execute(
            select(func.count(User.id)).where(
                User.last_active >= today_start
            )
        )
        active_users_today = active_users_result.scalar() or 0
        return {
            "total_users": total_users,
            "total_generations": total_generations,
            "total_deepfakes": total_deepfakes,
            "active_users_today": active_users_today
        }
user_service = UserService()
