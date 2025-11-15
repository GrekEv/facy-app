"""Сервис для работы с пользователями"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User
from datetime import datetime
from typing import Optional
import logging

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
            await session.commit()
            return user
        
        # Создаем нового пользователя
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        logger.info(f"Created new user: {telegram_id}")
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


user_service = UserService()

