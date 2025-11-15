"""API endpoints для платежей"""
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel

from database import get_session
from services.payment_service import PaymentService
from services.user_service import UserService

router = APIRouter(prefix="/api/payments", tags=["payments"])


class CreatePaymentRequest(BaseModel):
    """Запрос на создание платежа"""
    package_key: str  # 100, 500, 1000, 2500
    payment_provider: str  # telegram, stripe, yookassa, crypto, google_pay, samsung_pay
    promo_code: Optional[str] = None


class PaymentResponse(BaseModel):
    """Ответ с данными платежа"""
    transaction_id: int
    amount: int
    price: float
    currency: str
    status: str
    payment_url: Optional[str] = None
    crypto_address: Optional[str] = None
    crypto_amount: Optional[float] = None
    crypto_currency: Optional[str] = None


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    request: CreatePaymentRequest,
    telegram_id: int = Form(...),
    session: AsyncSession = Depends(get_session)
):
    """Создать платеж"""
    try:
        # Получаем пользователя
        user = await UserService.get_user_by_telegram_id(session, telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Создаем платеж
        payment_data = await PaymentService.create_payment(
            session=session,
            user_id=user.id,
            package_key=request.package_key,
            payment_provider=request.payment_provider,
            promo_code=request.promo_code
        )
        
        # Если криптоплатеж, получаем адрес
        if request.payment_provider == "crypto":
            # Здесь должна быть логика получения адреса кошелька
            # Пока возвращаем базовые данные
            pass
        
        return PaymentResponse(
            transaction_id=payment_data["transaction_id"],
            amount=payment_data["amount"],
            price=payment_data["price"],
            currency=payment_data["currency"],
            status=payment_data["status"]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-crypto")
async def verify_crypto_payment(
    transaction_id: int = Form(...),
    tx_hash: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    """Проверить криптоплатеж"""
    try:
        success = await PaymentService.verify_crypto_payment(
            session=session,
            transaction_id=transaction_id,
            tx_hash=tx_hash
        )
        
        if success:
            return {"status": "success", "message": "Payment verified"}
        else:
            return {"status": "failed", "message": "Payment verification failed"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{transaction_id}")
async def get_payment_status(
    transaction_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Получить статус платежа"""
    status = await PaymentService.get_payment_status(session, transaction_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return status


@router.post("/webhook/telegram")
async def telegram_payment_webhook(
    # Здесь должна быть обработка webhook от Telegram Payments
    pass
):
    """Webhook для Telegram Payments"""
    pass


@router.post("/webhook/stripe")
async def stripe_payment_webhook(
    # Здесь должна быть обработка webhook от Stripe
    pass
):
    """Webhook для Stripe"""
    pass


@router.post("/webhook/yookassa")
async def yookassa_payment_webhook(
    # Здесь должна быть обработка webhook от YooKassa
    pass
):
    """Webhook для YooKassa"""
    pass

