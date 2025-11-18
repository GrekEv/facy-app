"""Модели базы данных"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language_code = Column(String, default="ru")
    
    # Баланс
    balance = Column(Integer, default=50)  # Стартовый бонус 50 поинтов
    free_generations = Column(Integer, default=1)  # 1 бесплатная генерация
    
    # Подписка
    is_premium = Column(Boolean, default=False)
    premium_until = Column(DateTime, nullable=True)
    plan_type = Column(String, default="basic")  # basic или standard
    plan_activated_at = Column(DateTime, nullable=True)
    
    # Ограничения тарифа (для базового тарифа)
    images_used = Column(Integer, default=0)  # Использовано изображений
    videos_used = Column(Integer, default=0)  # Использовано видео
    
    # Статистика
    total_generations = Column(Integer, default=0)
    total_deepfakes = Column(Integer, default=0)
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # KYC и безопасность
    kyc_status = Column(String, default="pending")  # pending, verified, rejected, blocked
    kyc_verified_at = Column(DateTime, nullable=True)
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(Text, nullable=True)
    
    # Реферальная система
    referral_code = Column(String, unique=True, nullable=True, index=True)
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    referral_balance = Column(Float, default=0.0)  # Заработанные на рефералах
    
    # Email авторизация и подтверждение
    email = Column(String, nullable=True, index=True)
    email_verified = Column(Boolean, default=False)
    verification_code = Column(String, nullable=True)
    verification_code_expires = Column(DateTime, nullable=True)
    
    # Минимальный вывод
    min_withdrawal = Column(Float, default=100.0)  # Минимальная сумма вывода
    
    # Связи
    generations = relationship("Generation", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    payment_methods = relationship("PaymentMethod", back_populates="user")
    withdrawals = relationship("Withdrawal", back_populates="user")


class Generation(Base):
    """Модель генерации (deepfake или изображение)"""
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Тип: 'deepfake' или 'image'
    generation_type = Column(String, nullable=False)
    
    # Параметры
    prompt = Column(Text, nullable=True)  # Для генерации изображений
    model = Column(String, nullable=True)  # Модель для генерации
    style = Column(String, nullable=True)  # Стиль
    
    # Файлы
    source_file = Column(String, nullable=True)  # Исходное фото
    target_file = Column(String, nullable=True)  # Целевое видео (для deepfake)
    result_file = Column(String, nullable=True)  # Результат
    
    # Статус
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Стоимость
    cost = Column(Integer, default=0)
    
    # Статистика
    likes = Column(Integer, default=0)
    views = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Модерация и жалобы
    is_moderated = Column(Boolean, default=False)
    moderation_status = Column(String, default="pending")  # pending, approved, rejected
    moderation_notes = Column(Text, nullable=True)
    reports_count = Column(Integer, default=0)
    
    # Связи
    user = relationship("User", back_populates="generations")
    reports = relationship("Report", back_populates="generation")


class Report(Base):
    """Модель жалобы на контент"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True)
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=False)
    reporter_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Причина жалобы
    reason = Column(String, nullable=False)  # nsfw, copyright, harassment, other
    description = Column(Text, nullable=True)
    
    # Статус обработки
    status = Column(String, default="pending")  # pending, reviewing, resolved, rejected
    admin_notes = Column(Text, nullable=True)
    processed_by = Column(Integer, nullable=True)  # ID администратора
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Связи
    generation = relationship("Generation", back_populates="reports")
    reporter = relationship("User", foreign_keys=[reporter_user_id])


class AuditLog(Base):
    """Модель лога аудита"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Действие
    action = Column(String, nullable=False)  # payment, withdrawal, generation, report, etc.
    action_type = Column(String, nullable=False)  # create, update, delete, approve, reject
    details = Column(Text, nullable=True)  # JSON с деталями
    
    # IP и User Agent
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Дата
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", foreign_keys=[user_id])


class RateLimit(Base):
    """Модель для rate limiting"""
    __tablename__ = "rate_limits"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Тип ограничения
    limit_type = Column(String, nullable=False)  # generation, payment, api_call
    count = Column(Integer, default=0)
    window_start = Column(DateTime, default=datetime.utcnow)
    
    # Дата
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User")


class Transaction(Base):
    """Модель транзакции (покупка поинтов)"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Сумма
    amount = Column(Integer, nullable=False)  # Количество поинтов
    price = Column(Float, nullable=False)  # Цена в рублях
    currency = Column(String, default="RUB")  # Валюта (RUB, USD, EUR, BTC, ETH и т.д.)
    
    # Статус
    status = Column(String, default="pending")  # pending, processing, completed, failed, refunded
    
    # Платежная система
    payment_provider = Column(String, nullable=False)  # telegram, stripe, yookassa, crypto, google_pay, samsung_pay
    payment_method = Column(String, nullable=True)  # card, crypto, wallet и т.д.
    payment_id = Column(String, nullable=True)  # ID платежа в платежной системе
    payment_url = Column(String, nullable=True)  # URL для оплаты (для крипты)
    
    # Криптовалюта (если используется)
    crypto_currency = Column(String, nullable=True)  # BTC, ETH, USDT и т.д.
    crypto_address = Column(String, nullable=True)  # Адрес для получения
    crypto_amount = Column(Float, nullable=True)  # Сумма в криптовалюте
    crypto_tx_hash = Column(String, nullable=True)  # Хеш транзакции
    
    # Промокод/скидка
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"), nullable=True)
    discount_amount = Column(Float, default=0.0)  # Сумма скидки
    
    # Метаданные
    transaction_metadata = Column(Text, nullable=True)  # JSON с дополнительными данными
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Для криптоплатежей
    
    # Связи
    user = relationship("User", back_populates="transactions")
    promo_code = relationship("PromoCode", back_populates="transactions")


class PromoCode(Base):
    """Модель промокода"""
    __tablename__ = "promo_codes"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    
    # Тип скидки: percent (процент) или fixed (фиксированная сумма)
    discount_type = Column(String, nullable=False)  # percent, fixed
    discount_value = Column(Float, nullable=False)  # Значение скидки
    
    # Ограничения
    max_uses = Column(Integer, nullable=True)  # Максимальное количество использований
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Срок действия
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    
    # Минимальная сумма заказа
    min_amount = Column(Float, nullable=True)
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)  # ID администратора
    
    # Связи
    transactions = relationship("Transaction", back_populates="promo_code")


class PaymentMethod(Base):
    """Модель платежного метода пользователя"""
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Тип метода
    method_type = Column(String, nullable=False)  # card, crypto, wallet
    provider = Column(String, nullable=False)  # telegram, stripe, yookassa, crypto
    
    # Данные (зашифрованные)
    encrypted_data = Column(Text, nullable=True)  # Зашифрованные данные карты/кошелька
    last_four = Column(String, nullable=True)  # Последние 4 цифры карты
    
    # Криптовалюта
    crypto_currency = Column(String, nullable=True)
    crypto_address = Column(String, nullable=True)
    
    # Статус
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="payment_methods")


class Withdrawal(Base):
    """Модель вывода средств"""
    __tablename__ = "withdrawals"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Сумма
    amount = Column(Float, nullable=False)  # Сумма в рублях
    currency = Column(String, default="RUB")
    
    # Метод вывода
    withdrawal_method = Column(String, nullable=False)  # card, crypto, wallet
    withdrawal_details = Column(Text, nullable=True)  # JSON с деталями
    
    # Статус
    status = Column(String, default="pending")  # pending, processing, completed, rejected, cancelled
    
    # Комиссия
    fee = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)  # Сумма после комиссии
    
    # Модерация
    admin_notes = Column(Text, nullable=True)
    processed_by = Column(Integer, nullable=True)  # ID администратора
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="withdrawals")

