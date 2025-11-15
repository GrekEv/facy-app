"""Обработчики платежей"""
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery, 
    Message, 
    PreCheckoutQuery, 
    SuccessfulPayment,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from database import get_session
from database.models import Transaction
from services import payment_service
from services.user_service import UserService
from config import settings
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

router = Router()


def get_payment_methods_keyboard(transaction_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора метода оплаты"""
    builder = InlineKeyboardBuilder()
    
    # Telegram Payments (встроенный)
    builder.row(
        InlineKeyboardButton(
            text="💳 Telegram Payments",
            callback_data=f"pay_telegram_{transaction_id}"
        )
    )
    
    # Карты (Visa, Mir)
    builder.row(
        InlineKeyboardButton(
            text="💳 Visa / Mir",
            callback_data=f"pay_card_{transaction_id}"
        )
    )
    
    # Google Pay / Samsung Pay
    builder.row(
        InlineKeyboardButton(
            text="📱 Google Pay / Samsung Pay",
            callback_data=f"pay_wallet_{transaction_id}"
        )
    )
    
    # Криптовалюта
    builder.row(
        InlineKeyboardButton(
            text="₿ Криптовалюта (BTC/ETH/USDT)",
            callback_data=f"pay_crypto_{transaction_id}"
        )
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="buy_points")
    )
    
    return builder.as_markup()


def get_crypto_methods_keyboard(transaction_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора криптовалюты"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="₿ Bitcoin (BTC)",
            callback_data=f"crypto_btc_{transaction_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Ξ Ethereum (ETH)",
            callback_data=f"crypto_eth_{transaction_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="₮ Tether (USDT)",
            callback_data=f"crypto_usdt_{transaction_id}"
        )
    )
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data=f"pay_methods_{transaction_id}")
    )
    
    return builder.as_markup()


@router.callback_query(F.data.startswith("buy_"))
async def process_buy_points(callback: CallbackQuery):
    """Обработка покупки поинтов - выбор метода оплаты"""
    amount_str = callback.data.replace("buy_", "")
    
    packages = {
        "100": {"points": 100, "price": 99},
        "500": {"points": 500, "price": 399},
        "1000": {"points": 1000, "price": 699},
        "2500": {"points": 2500, "price": 1499}
    }
    
    if amount_str not in packages:
        await callback.answer("❌ Неверный пакет", show_alert=True)
        return
    
    package = packages[amount_str]
    
    async for session in get_session():
        try:
            # Создание транзакции
            payment_data = await payment_service.PaymentService.create_payment(
                session=session,
                user_id=callback.from_user.id,
                package_key=amount_str,
                payment_provider="pending"  # Будет обновлен при выборе метода
            )
            
            transaction_id = payment_data["transaction_id"]
            
            text = f"""
💎 <b>Покупка {package['points']} поинтов</b>

💰 Стоимость: <b>{package['price']}₽</b>

Выберите способ оплаты:
"""
            
            await callback.message.edit_text(
                text,
                reply_markup=get_payment_methods_keyboard(transaction_id)
            )
            
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            await callback.answer("❌ Ошибка при создании платежа", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("pay_telegram_"))
async def process_telegram_payment(callback: CallbackQuery, bot):
    """Обработка платежа через Telegram Payments"""
    transaction_id = int(callback.data.replace("pay_telegram_", ""))
    
    async for session in get_session():
        result = await session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()
        
        if not transaction or transaction.user_id != callback.from_user.id:
            await callback.answer("❌ Транзакция не найдена", show_alert=True)
            return
        
        # Создание инвойса для Telegram Payments
        prices = [LabeledPrice(label=f"{transaction.amount} поинтов", amount=int(transaction.price * 100))]
        
        try:
            await bot.send_invoice(
                chat_id=callback.from_user.id,
                title=f"Покупка {transaction.amount} поинтов",
                description=f"Пополнение баланса на {transaction.amount} поинтов",
                payload=f"transaction_{transaction_id}",
                provider_token=settings.STRIPE_SECRET_KEY or "TEST",  # Нужен реальный токен
                currency="RUB",
                prices=prices,
                start_parameter=f"transaction_{transaction_id}",
                need_name=False,
                need_phone_number=False,
                need_email=False,
                need_shipping_address=False
            )
            
            await callback.answer()
        except Exception as e:
            logger.error(f"Error sending invoice: {e}")
            await callback.answer("❌ Ошибка при создании платежа", show_alert=True)


@router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery, bot):
    """Обработка предварительной проверки платежа"""
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    """Обработка успешного платежа"""
    payment = message.successful_payment
    transaction_id = int(payment.invoice_payload.replace("transaction_", ""))
    
    async for session in get_session():
        success = await payment_service.PaymentService.process_telegram_payment(
            session=session,
            transaction_id=transaction_id,
            payment_id=payment.telegram_payment_charge_id,
            provider_payment_charge_id=payment.provider_payment_charge_id
        )
        
        if success:
            user = await UserService.get_user_by_telegram_id(session, message.from_user.id)
            await message.answer(
                f"✅ Платеж успешно обработан!\n\n"
                f"💎 Начислено: {payment.total_amount / 100} поинтов\n"
                f"💰 Ваш баланс: {user.balance if user else 0} поинтов"
            )
        else:
            await message.answer("❌ Ошибка при обработке платежа")


@router.callback_query(F.data.startswith("pay_crypto_"))
async def process_crypto_payment(callback: CallbackQuery):
    """Обработка выбора криптоплатежа"""
    transaction_id = int(callback.data.replace("pay_crypto_", ""))
    
    await callback.message.edit_text(
        "Выберите криптовалюту:",
        reply_markup=get_crypto_methods_keyboard(transaction_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("crypto_"))
async def process_crypto_method(callback: CallbackQuery):
    """Обработка выбора конкретной криптовалюты"""
    parts = callback.data.split("_")
    crypto_currency = parts[1].upper()  # BTC, ETH, USDT
    transaction_id = int(parts[2])
    
    async for session in get_session():
        try:
            # Получаем адрес кошелька из настроек
            wallet_address = None
            if crypto_currency == "BTC":
                wallet_address = settings.CRYPTO_WALLET_ADDRESS_BTC
            elif crypto_currency == "ETH":
                wallet_address = settings.CRYPTO_WALLET_ADDRESS_ETH
            elif crypto_currency == "USDT":
                wallet_address = settings.CRYPTO_WALLET_ADDRESS_USDT
            
            if not wallet_address:
                await callback.answer("❌ Криптовалюта не настроена", show_alert=True)
                return
            
            # Здесь должна быть логика конвертации цены в криптовалюту
            # Пока используем примерные значения
            result = await session.execute(
                select(Transaction).where(Transaction.id == transaction_id)
            )
            transaction = result.scalar_one_or_none()
            
            if not transaction:
                await callback.answer("❌ Транзакция не найдена", show_alert=True)
                return
            
            # Создание криптоплатежа
            crypto_data = await payment_service.PaymentService.process_crypto_payment(
                session=session,
                transaction_id=transaction_id,
                crypto_currency=crypto_currency,
                crypto_address=wallet_address,
                crypto_amount=transaction.price / 50000.0  # Примерный курс (нужно получать реальный)
            )
            
            text = f"""
💎 <b>Оплата криптовалютой</b>

💰 Сумма: <b>{transaction.price}₽</b>
₿ Валюта: <b>{crypto_currency}</b>
📝 Адрес: <code>{crypto_data['address']}</code>
💵 К оплате: <b>{crypto_data['amount']} {crypto_currency}</b>

⚠️ <b>Важно:</b>
• Отправьте точную сумму на указанный адрес
• После отправки транзакция будет проверена автоматически
• Обычно это занимает 10-30 минут
• Срок действия: 24 часа

После отправки нажмите "Подтвердить оплату"
"""
            
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="✅ Подтвердить оплату",
                    callback_data=f"confirm_crypto_{transaction_id}"
                )
            )
            builder.row(
                InlineKeyboardButton(text="🔙 Назад", callback_data="buy_points")
            )
            
            await callback.message.edit_text(text, reply_markup=builder.as_markup())
            
        except Exception as e:
            logger.error(f"Error processing crypto payment: {e}")
            await callback.answer("❌ Ошибка при создании платежа", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("pay_card_"))
async def process_card_payment(callback: CallbackQuery):
    """Обработка оплаты картой (Visa/Mir через YooKassa)"""
    transaction_id = int(callback.data.replace("pay_card_", ""))
    
    # Здесь должна быть интеграция с YooKassa
    # Пока что показываем сообщение
    await callback.answer(
        "💳 Оплата картой будет доступна после настройки YooKassa",
        show_alert=True
    )


@router.callback_query(F.data.startswith("pay_wallet_"))
async def process_wallet_payment(callback: CallbackQuery):
    """Обработка оплаты через Google Pay / Samsung Pay"""
    transaction_id = int(callback.data.replace("pay_wallet_", ""))
    
    # Здесь должна быть интеграция с Google Pay / Samsung Pay
    # Пока что показываем сообщение
    await callback.answer(
        "📱 Оплата через Google Pay / Samsung Pay будет доступна после настройки",
        show_alert=True
    )

