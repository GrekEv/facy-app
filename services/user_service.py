"""Сервис для работы с пользователями"""
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
    """Сервис для управления пользователями"""
    
    @staticmethod
    async def get_or_create_user(
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "ru"
    ) -> User:
        """
        Получить или создать пользователя
        
        Args:
            session: Сессия БД
            telegram_id: ID пользователя в Telegram
            username: Username пользователя
            first_name: Имя
            last_name: Фамилия
            language_code: Код языка
            
        Returns:
            Объект пользователя
        """
        # Ищем существующего пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Обновляем время последней активности
            user.last_active = datetime.utcnow()
            # Генерируем реферальный код, если его нет
            if not user.referral_code:
                new_referral_code = UserService.generate_referral_code()
                # Проверяем уникальность
                while True:
                    check_result = await session.execute(
                        select(User).where(User.referral_code == new_referral_code)
                    )
                    if check_result.scalar_one_or_none() is None:
                        break
                    new_referral_code = UserService.generate_referral_code()
                user.referral_code = new_referral_code
                await session.commit()
                await session.refresh(user)  # Обновляем объект после commit
                logger.info(f"Generated referral_code {new_referral_code} for existing user {telegram_id}")
            else:
                await session.commit()
            return user
        
        # Генерируем уникальный реферальный код для нового пользователя
        new_referral_code = UserService.generate_referral_code()
        # Проверяем уникальность
        while True:
            check_result = await session.execute(
                select(User).where(User.referral_code == new_referral_code)
            )
            if check_result.scalar_one_or_none() is None:
                break
            new_referral_code = UserService.generate_referral_code()
        
        # Создаем нового пользователя
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
        """Получить пользователя по ID"""
        return await session.get(User, user_id)
    
    @staticmethod
    async def get_user_by_telegram_id(
        session: AsyncSession,
        telegram_id: int
    ) -> Optional[User]:
        """
        Получить пользователя по Telegram ID
        
        Args:
            session: Сессия БД
            telegram_id: ID пользователя в Telegram
            
        Returns:
            Объект пользователя или None
        """
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
        """
        Обновить баланс пользователя
        
        Args:
            session: Сессия БД
            user: Пользователь
            amount: Изменение баланса (может быть отрицательным)
            
        Returns:
            True если успешно, False если недостаточно средств
        """
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
        """
        Проверить, может ли пользователь позволить себе операцию
        
        Args:
            user: Пользователь
            cost: Стоимость операции
            
        Returns:
            True если хватает средств
        """
        return user.balance >= cost or user.free_generations > 0
    
    @staticmethod
    def generate_referral_code() -> str:
        """Генерирует уникальный реферальный код"""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(8))
    
    @staticmethod
    def generate_verification_code() -> str:
        """Генерирует 6-значный код подтверждения"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    @staticmethod
    async def send_verification_code(
        session: AsyncSession,
        telegram_id: int,
        email: str
    ) -> tuple[bool, Optional[str]]:
        """
        Отправить код подтверждения на email
        
        Args:
            session: Сессия БД
            telegram_id: ID пользователя в Telegram
            email: Email для отправки кода
            
        Returns:
            (success, error_message)
        """
        from services.email_service import EmailService
        
        # Валидация email
        if not EmailService.validate_email(email):
            return False, "Неверный формат email"
        
        # Получаем или создаем пользователя
        user = await UserService.get_or_create_user(
            session,
            telegram_id=telegram_id
        )
        
        # Генерируем код
        code = UserService.generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Сохраняем код в БД
        user.email = email.lower().strip()
        user.verification_code = code
        user.verification_code_expires = expires_at
        user.email_verified = False  # Сбрасываем статус подтверждения
        
        await session.commit()
        
        # Отправляем email
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
        """
        Проверить код подтверждения email
        
        Args:
            session: Сессия БД
            telegram_id: ID пользователя в Telegram
            code: Код подтверждения
            
        Returns:
            (success, error_message)
        """
        # Получаем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False, "Пользователь не найден"
        
        # Проверяем код
        if not user.verification_code:
            return False, "Код подтверждения не был отправлен"
        
        if user.verification_code != code:
            return False, "Неверный код подтверждения"
        
        if user.verification_code_expires and user.verification_code_expires < datetime.utcnow():
            return False, "Код подтверждения истек. Запросите новый код."
        
        # Подтверждаем email
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
        """
        Создать пользователя с обработкой реферального кода
        
        Args:
            session: Сессия БД
            telegram_id: ID пользователя в Telegram
            username: Username пользователя
            first_name: Имя
            last_name: Фамилия
            language_code: Код языка
            referral_code: Реферальный код (опционально)
            
        Returns:
            Объект пользователя
        """
        # Проверяем, существует ли пользователь
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            existing_user.last_active = datetime.utcnow()
            await session.commit()
            return existing_user
        
        # Обрабатываем реферальный код
        referred_by_id = None
        if referral_code:
            ref_result = await session.execute(
                select(User).where(User.referral_code == referral_code)
            )
            referrer = ref_result.scalar_one_or_none()
            if referrer:
                referred_by_id = referrer.id
                # Начисляем бонус рефереру (например, +10 поинтов)
                referrer.referral_balance += 10.0
                logger.info(f"User {referrer.telegram_id} referred new user {telegram_id}")
        
        # Генерируем уникальный реферальный код для нового пользователя
        new_referral_code = UserService.generate_referral_code()
        # Проверяем уникальность
        while True:
            check_result = await session.execute(
                select(User).where(User.referral_code == new_referral_code)
            )
            if check_result.scalar_one_or_none() is None:
                break
            new_referral_code = UserService.generate_referral_code()
        
        # Создаем нового пользователя
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
        """
        Получить статистику системы
        
        Returns:
            Словарь со статистикой
        """
        # Общее количество пользователей
        total_users_result = await session.execute(
            select(func.count(User.id))
        )
        total_users = total_users_result.scalar() or 0
        
        # Общее количество генераций
        total_generations_result = await session.execute(
            select(func.sum(User.total_generations))
        )
        total_generations = total_generations_result.scalar() or 0
        
        # Общее количество deepfakes
        total_deepfakes_result = await session.execute(
            select(func.sum(User.total_deepfakes))
        )
        total_deepfakes = total_deepfakes_result.scalar() or 0
        
        # Активные пользователи за сегодня
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

