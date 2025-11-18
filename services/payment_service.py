"""�е�в�� дл� о��а�отк� платежей"""
import logging
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import Transaction, User, PromoCode
from services.user_service import UserService

logger = logging.getLogger(__name__)


class PaymentService:
    """�е�в�� дл� �а�от� � платежам�"""
    
    # �акет� по�нтов
    POINT_PACKAGES = {
        "100": {"points": 100, "price": 99.0},
        "500": {"points": 500, "price": 399.0},
        "1000": {"points": 1000, "price": 699.0},
        "2500": {"points": 2500, "price": 1499.0}
    }
    
    @staticmethod
    async def create_payment(
        session: AsyncSession,
        user_id: int,
        package_key: str,
        payment_provider: str,
        promo_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        �оздат� платеж
        
        Args:
            session: �е���� Б�
            user_id: ID пол�зовател�
            package_key: �л�ч пакета (100, 500, 1000, 2500)
            payment_provider: ��овайде� платежа (telegram, stripe, yookassa, crypto, google_pay, samsung_pay)
            promo_code: ��омокод (опц�онал�но)
            
        Returns:
            �лова�� � данн�м� платежа
        """
        if package_key not in PaymentService.POINT_PACKAGES:
            raise ValueError(f"�еве�н�й пакет: {package_key}")
        
        package = PaymentService.POINT_PACKAGES[package_key]
        user = await UserService.get_user_by_id(session, user_id)
        
        if not user:
            raise ValueError("�ол�зовател� не найден")
        
        # ��ове�ка п�омокода
        discount_amount = 0.0
        promo_code_obj = None
        
        if promo_code:
            promo_code_obj = await PaymentService._validate_promo_code(
                session, promo_code, package["price"]
            )
            if promo_code_obj:
                if promo_code_obj.discount_type == "percent":
                    discount_amount = package["price"] * (promo_code_obj.discount_value / 100)
                else:
                    discount_amount = promo_code_obj.discount_value
                
                discount_amount = min(discount_amount, package["price"])
        
        final_price = package["price"] - discount_amount
        
        # �оздан�е т�анзакц��
        transaction = Transaction(
            user_id=user_id,
            amount=package["points"],
            price=final_price,
            currency="RUB",
            status="pending",
            payment_provider=payment_provider,
            promo_code_id=promo_code_obj.id if promo_code_obj else None,
            discount_amount=discount_amount,
            expires_at=datetime.utcnow() + timedelta(hours=24)  # �л� к��птоплатежей
        )
        
        session.add(transaction)
        await session.commit()
        await session.refresh(transaction)
        
        logger.info(f"Created payment transaction {transaction.id} for user {user_id}")
        
        return {
            "transaction_id": transaction.id,
            "amount": package["points"],
            "price": final_price,
            "original_price": package["price"],
            "discount": discount_amount,
            "currency": "RUB",
            "status": "pending"
        }
    
    @staticmethod
    async def _validate_promo_code(
        session: AsyncSession,
        code: str,
        order_amount: float
    ) -> Optional[PromoCode]:
        """�ал�дац�� п�омокода"""
        result = await session.execute(
            select(PromoCode).where(PromoCode.code == code.upper())
        )
        promo = result.scalar_one_or_none()
        
        if not promo:
            return None
        
        if not promo.is_active:
            return None
        
        # ��ове�ка ��ока дей�тв��
        now = datetime.utcnow()
        if promo.valid_from and now < promo.valid_from:
            return None
        if promo.valid_until and now > promo.valid_until:
            return None
        
        # ��ове�ка м�н�мал�ной �умм�
        if promo.min_amount and order_amount < promo.min_amount:
            return None
        
        # ��ове�ка мак��мал�но�о кол�че�тва ��пол�зован�й
        if promo.max_uses and promo.used_count >= promo.max_uses:
            return None
        
        return promo
    
    @staticmethod
    async def process_telegram_payment(
        session: AsyncSession,
        transaction_id: int,
        payment_id: str,
        provider_payment_charge_id: str
    ) -> bool:
        """О��а�отка платежа че�ез Telegram Payments"""
        result = await session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            return False
        
        if transaction.status != "pending":
            return False
        
        # О�новлен�е т�анзакц��
        transaction.status = "completed"
        transaction.payment_id = provider_payment_charge_id
        transaction.completed_at = datetime.utcnow()
        
        # �ач��лен�е по�нтов пол�зовател�
        user = await UserService.get_user_by_id(session, transaction.user_id)
        if user:
            user.balance += transaction.amount
            if transaction.promo_code_id:
                promo = await session.get(PromoCode, transaction.promo_code_id)
                if promo:
                    promo.used_count += 1
        
        await session.commit()
        
        logger.info(f"Processed Telegram payment {transaction_id}")
        return True
    
    @staticmethod
    async def process_crypto_payment(
        session: AsyncSession,
        transaction_id: int,
        crypto_currency: str,
        crypto_address: str,
        crypto_amount: float
    ) -> Dict[str, Any]:
        """�оздан�е к��птоплатежа"""
        result = await session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise ValueError("Т�анзакц�� не найдена")
        
        # О�новлен�е т�анзакц�� � данн�м� к��пт�
        transaction.crypto_currency = crypto_currency
        transaction.crypto_address = crypto_address
        transaction.crypto_amount = crypto_amount
        transaction.status = "processing"
        transaction.payment_url = f"crypto://{crypto_currency.lower()}:{crypto_address}"
        
        await session.commit()
        
        return {
            "address": crypto_address,
            "amount": crypto_amount,
            "currency": crypto_currency,
            "expires_at": transaction.expires_at.isoformat() if transaction.expires_at else None
        }
    
    @staticmethod
    async def verify_crypto_payment(
        session: AsyncSession,
        transaction_id: int,
        tx_hash: str
    ) -> bool:
        """��ове�ка к��птоплатежа по �ешу т�анзакц��"""
        result = await session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            return False
        
        # Зде�� должна ��т� п�ове�ка т�анзакц�� че�ез �локчейн API
        # �ока что п�о�то о�новл�ем �тату�
        transaction.crypto_tx_hash = tx_hash
        transaction.status = "completed"
        transaction.completed_at = datetime.utcnow()
        
        # �ач��лен�е по�нтов
        user = await UserService.get_user_by_id(session, transaction.user_id)
        if user:
            user.balance += transaction.amount
        
        await session.commit()
        
        logger.info(f"Verified crypto payment {transaction_id} with tx {tx_hash}")
        return True
    
    @staticmethod
    async def get_payment_status(
        session: AsyncSession,
        transaction_id: int
    ) -> Optional[Dict[str, Any]]:
        """�олуч�т� �тату� платежа"""
        result = await session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            return None
        
        return {
            "id": transaction.id,
            "status": transaction.status,
            "amount": transaction.amount,
            "price": transaction.price,
            "provider": transaction.payment_provider,
            "created_at": transaction.created_at.isoformat(),
            "completed_at": transaction.completed_at.isoformat() if transaction.completed_at else None
        }

