"""�одел� �аз� данн��"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(DeclarativeBase):
    """Базов�й кла�� дл� в�е� моделей"""
    pass


class User(Base):
    """�одел� пол�зовател�"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language_code = Column(String, default="ru")
    
    # Балан�
    balance = Column(Integer, default=50)  # �та�тов�й �ону� 50 по�нтов
    free_generations = Column(Integer, default=1)  # 1 �е�платна� �ене�ац��
    
    # �одп��ка
    is_premium = Column(Boolean, default=False)
    premium_until = Column(DateTime, nullable=True)
    plan_type = Column(String, default="basic")  # basic �л� standard
    plan_activated_at = Column(DateTime, nullable=True)
    
    # О��ан�чен�� та��фа (дл� �азово�о та��фа)
    images_used = Column(Integer, default=0)  # И�пол�зовано �зо��ажен�й
    videos_used = Column(Integer, default=0)  # И�пол�зовано в�део
    
    # �тат��т�ка
    total_generations = Column(Integer, default=0)
    total_deepfakes = Column(Integer, default=0)
    
    # �ат�
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # KYC � �езопа�но�т�
    kyc_status = Column(String, default="pending")  # pending, verified, rejected, blocked
    kyc_verified_at = Column(DateTime, nullable=True)
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(Text, nullable=True)
    
    # �ефе�ал�на� ���тема
    referral_code = Column(String, unique=True, nullable=True, index=True)
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    referral_balance = Column(Float, default=0.0)  # За�а�отанн�е на �ефе�ала�
    
    # Email авто��зац�� � подтве�жден�е
    email = Column(String, nullable=True, index=True)
    email_verified = Column(Boolean, default=False)
    verification_code = Column(String, nullable=True)
    verification_code_expires = Column(DateTime, nullable=True)
    
    # ��н�мал�н�й в�вод
    min_withdrawal = Column(Float, default=100.0)  # ��н�мал�на� �умма в�вода
    
    # �в�з�
    generations = relationship("Generation", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    payment_methods = relationship("PaymentMethod", back_populates="user")
    withdrawals = relationship("Withdrawal", back_populates="user")


class Generation(Base):
    """�одел� �ене�ац�� (deepfake �л� �зо��ажен�е)"""
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Т�п: 'deepfake' �л� 'image'
    generation_type = Column(String, nullable=False)
    
    # �а�амет��
    prompt = Column(Text, nullable=True)  # �л� �ене�ац�� �зо��ажен�й
    model = Column(String, nullable=True)  # �одел� дл� �ене�ац��
    style = Column(String, nullable=True)  # �т�л�
    
    # Файл�
    source_file = Column(String, nullable=True)  # И��одное фото
    target_file = Column(String, nullable=True)  # Целевое в�део (дл� deepfake)
    result_file = Column(String, nullable=True)  # �езул�тат
    
    # �тату�
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # �то�мо�т�
    cost = Column(Integer, default=0)
    
    # �тат��т�ка
    likes = Column(Integer, default=0)
    views = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    
    # �ат�
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # �оде�ац�� � жало��
    is_moderated = Column(Boolean, default=False)
    moderation_status = Column(String, default="pending")  # pending, approved, rejected
    moderation_notes = Column(Text, nullable=True)
    reports_count = Column(Integer, default=0)
    
    # �в�з�
    user = relationship("User", back_populates="generations")
    reports = relationship("Report", back_populates="generation")


class Report(Base):
    """�одел� жало�� на контент"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True)
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=False)
    reporter_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # ���ч�на жало��
    reason = Column(String, nullable=False)  # nsfw, copyright, harassment, other
    description = Column(Text, nullable=True)
    
    # �тату� о��а�отк�
    status = Column(String, default="pending")  # pending, reviewing, resolved, rejected
    admin_notes = Column(Text, nullable=True)
    processed_by = Column(Integer, nullable=True)  # ID адм�н��т�ато�а
    
    # �ат�
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # �в�з�
    generation = relationship("Generation", back_populates="reports")
    reporter = relationship("User", foreign_keys=[reporter_user_id])


class AuditLog(Base):
    """�одел� ло�а ауд�та"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # �ей�тв�е
    action = Column(String, nullable=False)  # payment, withdrawal, generation, report, etc.
    action_type = Column(String, nullable=False)  # create, update, delete, approve, reject
    details = Column(Text, nullable=True)  # JSON � детал�м�
    
    # IP � User Agent
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # �ата
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # �в�з�
    user = relationship("User", foreign_keys=[user_id])


class RateLimit(Base):
    """�одел� дл� rate limiting"""
    __tablename__ = "rate_limits"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Т�п о��ан�чен��
    limit_type = Column(String, nullable=False)  # generation, payment, api_call
    count = Column(Integer, default=0)
    window_start = Column(DateTime, default=datetime.utcnow)
    
    # �ата
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # �в�з�
    user = relationship("User")


class Transaction(Base):
    """�одел� т�анзакц�� (покупка по�нтов)"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # �умма
    amount = Column(Integer, nullable=False)  # �ол�че�тво по�нтов
    price = Column(Float, nullable=False)  # Цена в �у�л��
    currency = Column(String, default="RUB")  # �ал�та (RUB, USD, EUR, BTC, ETH � т.д.)
    
    # �тату�
    status = Column(String, default="pending")  # pending, processing, completed, failed, refunded
    
    # �латежна� ���тема
    payment_provider = Column(String, nullable=False)  # telegram, stripe, yookassa, crypto, google_pay, samsung_pay
    payment_method = Column(String, nullable=True)  # card, crypto, wallet � т.д.
    payment_id = Column(String, nullable=True)  # ID платежа в платежной ���теме
    payment_url = Column(String, nullable=True)  # URL дл� оплат� (дл� к��пт�)
    
    # ���птовал�та (е�л� ��пол�зует��)
    crypto_currency = Column(String, nullable=True)  # BTC, ETH, USDT � т.д.
    crypto_address = Column(String, nullable=True)  # �д�е� дл� получен��
    crypto_amount = Column(Float, nullable=True)  # �умма в к��птовал�те
    crypto_tx_hash = Column(String, nullable=True)  # �еш т�анзакц��
    
    # ��омокод/�к�дка
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"), nullable=True)
    discount_amount = Column(Float, default=0.0)  # �умма �к�дк�
    
    # �етаданн�е
    transaction_metadata = Column(Text, nullable=True)  # JSON � дополн�тел�н�м� данн�м�
    
    # �ат�
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # �л� к��птоплатежей
    
    # �в�з�
    user = relationship("User", back_populates="transactions")
    promo_code = relationship("PromoCode", back_populates="transactions")


class PromoCode(Base):
    """�одел� п�омокода"""
    __tablename__ = "promo_codes"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    
    # Т�п �к�дк�: percent (п�оцент) �л� fixed (ф�к���ованна� �умма)
    discount_type = Column(String, nullable=False)  # percent, fixed
    discount_value = Column(Float, nullable=False)  # Значен�е �к�дк�
    
    # О��ан�чен��
    max_uses = Column(Integer, nullable=True)  # �ак��мал�ное кол�че�тво ��пол�зован�й
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # ��ок дей�тв��
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    
    # ��н�мал�на� �умма заказа
    min_amount = Column(Float, nullable=True)
    
    # �ат�
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)  # ID адм�н��т�ато�а
    
    # �в�з�
    transactions = relationship("Transaction", back_populates="promo_code")


class PaymentMethod(Base):
    """�одел� платежно�о метода пол�зовател�"""
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Т�п метода
    method_type = Column(String, nullable=False)  # card, crypto, wallet
    provider = Column(String, nullable=False)  # telegram, stripe, yookassa, crypto
    
    # �анн�е (заш�ф�ованн�е)
    encrypted_data = Column(Text, nullable=True)  # Заш�ф�ованн�е данн�е ка�т�/кошел�ка
    last_four = Column(String, nullable=True)  # �о�ледн�е 4 ц�ф�� ка�т�
    
    # ���птовал�та
    crypto_currency = Column(String, nullable=True)
    crypto_address = Column(String, nullable=True)
    
    # �тату�
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # �ат�
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    
    # �в�з�
    user = relationship("User", back_populates="payment_methods")


class Withdrawal(Base):
    """�одел� в�вода ��ед�тв"""
    __tablename__ = "withdrawals"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # �умма
    amount = Column(Float, nullable=False)  # �умма в �у�л��
    currency = Column(String, default="RUB")
    
    # �етод в�вода
    withdrawal_method = Column(String, nullable=False)  # card, crypto, wallet
    withdrawal_details = Column(Text, nullable=True)  # JSON � детал�м�
    
    # �тату�
    status = Column(String, default="pending")  # pending, processing, completed, rejected, cancelled
    
    # �ом�����
    fee = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)  # �умма по�ле ком�����
    
    # �оде�ац��
    admin_notes = Column(Text, nullable=True)
    processed_by = Column(Integer, nullable=True)  # ID адм�н��т�ато�а
    
    # �ат�
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # �в�з�
    user = relationship("User", back_populates="withdrawals")

