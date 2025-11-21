# -*- coding: utf-8 -*-
"""Модели базы данных"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(DeclarativeBase):
    """ÐÐ°Ð·Ð¾Ð²ÑÐ¹ ÐºÐ»Ð°ÑÑ Ð´Ð»Ñ Ð²ÑÐµÑ Ð¼Ð¾Ð´ÐµÐ»ÐµÐ¹"""
    pass


class User(Base):
    """ÐÐ¾Ð´ÐµÐ»Ñ Ð¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°ÑÐµÐ»Ñ"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language_code = Column(String, default="ru")
    
    # ÐÐ°Ð»Ð°Ð½Ñ
    balance = Column(Integer, default=50)  # ÐÑÐ°ÑÑÐ¾Ð²ÑÐ¹ ÐÐ¾Ð½ÑÑ 50 Ð¿Ð¾ÐÐ½ÑÐ¾Ð²
    free_generations = Column(Integer, default=1)  # 1 ÐÐµÑÐ¿Ð»Ð°ÑÐ½Ð°Ñ ÐÐµÐ½ÐµÑÐ°ÑÐÑ
    
    # ÐÐ¾Ð´Ð¿ÐÑÐºÐ°
    is_premium = Column(Boolean, default=False)
    premium_until = Column(DateTime, nullable=True)
    plan_type = Column(String, default="basic")  # basic ÐÐ»Ð standard
    plan_activated_at = Column(DateTime, nullable=True)
    
    # ÐÐÑÐ°Ð½ÐÑÐµÐ½ÐÑ ÑÐ°ÑÐÑÐ° (Ð´Ð»Ñ ÐÐ°Ð·Ð¾Ð²Ð¾ÐÐ¾ ÑÐ°ÑÐÑÐ°)
    images_used = Column(Integer, default=0)  # ÐÑÐ¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°Ð½Ð¾ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐ¹
    videos_used = Column(Integer, default=0)  # ÐÑÐ¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°Ð½Ð¾ Ð²ÐÐ´ÐµÐ¾
    
    # ÐÑÐ°ÑÐÑÑÐÐºÐ°
    total_generations = Column(Integer, default=0)
    total_deepfakes = Column(Integer, default=0)
    
    # ÐÐ°ÑÑ
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # KYC Ð ÐÐµÐ·Ð¾Ð¿Ð°ÑÐ½Ð¾ÑÑÑ
    kyc_status = Column(String, default="pending")  # pending, verified, rejected, blocked
    kyc_verified_at = Column(DateTime, nullable=True)
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(Text, nullable=True)
    
    # ÐÐµÑÐµÑÐ°Ð»ÑÐ½Ð°Ñ ÑÐÑÑÐµÐ¼Ð°
    referral_code = Column(String, unique=True, nullable=True, index=True)
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    referral_balance = Column(Float, default=0.0)  # ÐÐ°ÑÐ°ÐÐ¾ÑÐ°Ð½Ð½ÑÐµ Ð½Ð° ÑÐµÑÐµÑÐ°Ð»Ð°Ñ
    
    # Email Ð°Ð²ÑÐ¾ÑÐÐ·Ð°ÑÐÑ Ð Ð¿Ð¾Ð´ÑÐ²ÐµÑÐ¶Ð´ÐµÐ½ÐÐµ
    email = Column(String, nullable=True, index=True)
    email_verified = Column(Boolean, default=False)
    verification_code = Column(String, nullable=True)
    verification_code_expires = Column(DateTime, nullable=True)
    
    # ÐÐÐ½ÐÐ¼Ð°Ð»ÑÐ½ÑÐ¹ Ð²ÑÐ²Ð¾Ð´
    min_withdrawal = Column(Float, default=100.0)  # ÐÐÐ½ÐÐ¼Ð°Ð»ÑÐ½Ð°Ñ ÑÑÐ¼Ð¼Ð° Ð²ÑÐ²Ð¾Ð´Ð°
    
    # ÐÐ²ÑÐ·Ð
    generations = relationship("Generation", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    payment_methods = relationship("PaymentMethod", back_populates="user")
    withdrawals = relationship("Withdrawal", back_populates="user")


class Generation(Base):
    """ÐÐ¾Ð´ÐµÐ»Ñ ÐÐµÐ½ÐµÑÐ°ÑÐÐ (deepfake ÐÐ»Ð ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐµ)"""
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Ð¢ÐÐ¿: 'deepfake' ÐÐ»Ð 'image'
    generation_type = Column(String, nullable=False)
    
    # ÐÐ°ÑÐ°Ð¼ÐµÑÑÑ
    prompt = Column(Text, nullable=True)  # ÐÐ»Ñ ÐÐµÐ½ÐµÑÐ°ÑÐÐ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÐ¹
    model = Column(String, nullable=True)  # ÐÐ¾Ð´ÐµÐ»Ñ Ð´Ð»Ñ ÐÐµÐ½ÐµÑÐ°ÑÐÐ
    style = Column(String, nullable=True)  # ÐÑÐÐ»Ñ
    
    # Ð¤Ð°Ð¹Ð»Ñ
    source_file = Column(String, nullable=True)  # ÐÑÑÐ¾Ð´Ð½Ð¾Ðµ ÑÐ¾ÑÐ¾
    target_file = Column(String, nullable=True)  # Ð¦ÐµÐ»ÐµÐ²Ð¾Ðµ Ð²ÐÐ´ÐµÐ¾ (Ð´Ð»Ñ deepfake)
    result_file = Column(String, nullable=True)  # ÐÐµÐ·ÑÐ»ÑÑÐ°Ñ
    
    # ÐÑÐ°ÑÑÑ
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # ÐÑÐ¾ÐÐ¼Ð¾ÑÑÑ
    cost = Column(Integer, default=0)
    
    # ÐÑÐ°ÑÐÑÑÐÐºÐ°
    likes = Column(Integer, default=0)
    views = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    
    # ÐÐ°ÑÑ
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # ÐÐ¾Ð´ÐµÑÐ°ÑÐÑ Ð Ð¶Ð°Ð»Ð¾ÐÑ
    is_moderated = Column(Boolean, default=False)
    moderation_status = Column(String, default="pending")  # pending, approved, rejected
    moderation_notes = Column(Text, nullable=True)
    reports_count = Column(Integer, default=0)
    
    # ÐÐ²ÑÐ·Ð
    user = relationship("User", back_populates="generations")
    reports = relationship("Report", back_populates="generation")


class Report(Base):
    """ÐÐ¾Ð´ÐµÐ»Ñ Ð¶Ð°Ð»Ð¾ÐÑ Ð½Ð° ÐºÐ¾Ð½ÑÐµÐ½Ñ"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True)
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=False)
    reporter_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # ÐÑÐÑÐÐ½Ð° Ð¶Ð°Ð»Ð¾ÐÑ
    reason = Column(String, nullable=False)  # nsfw, copyright, harassment, other
    description = Column(Text, nullable=True)
    
    # ÐÑÐ°ÑÑÑ Ð¾ÐÑÐ°ÐÐ¾ÑÐºÐ
    status = Column(String, default="pending")  # pending, reviewing, resolved, rejected
    admin_notes = Column(Text, nullable=True)
    processed_by = Column(Integer, nullable=True)  # ID Ð°Ð´Ð¼ÐÐ½ÐÑÑÑÐ°ÑÐ¾ÑÐ°
    
    # ÐÐ°ÑÑ
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # ÐÐ²ÑÐ·Ð
    generation = relationship("Generation", back_populates="reports")
    reporter = relationship("User", foreign_keys=[reporter_user_id])


class AuditLog(Base):
    """ÐÐ¾Ð´ÐµÐ»Ñ Ð»Ð¾ÐÐ° Ð°ÑÐ´ÐÑÐ°"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # ÐÐµÐ¹ÑÑÐ²ÐÐµ
    action = Column(String, nullable=False)  # payment, withdrawal, generation, report, etc.
    action_type = Column(String, nullable=False)  # create, update, delete, approve, reject
    details = Column(Text, nullable=True)  # JSON Ñ Ð´ÐµÑÐ°Ð»ÑÐ¼Ð
    
    # IP Ð User Agent
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # ÐÐ°ÑÐ°
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # ÐÐ²ÑÐ·Ð
    user = relationship("User", foreign_keys=[user_id])


class RateLimit(Base):
    """ÐÐ¾Ð´ÐµÐ»Ñ Ð´Ð»Ñ rate limiting"""
    __tablename__ = "rate_limits"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Ð¢ÐÐ¿ Ð¾ÐÑÐ°Ð½ÐÑÐµÐ½ÐÑ
    limit_type = Column(String, nullable=False)  # generation, payment, api_call
    count = Column(Integer, default=0)
    window_start = Column(DateTime, default=datetime.utcnow)
    
    # ÐÐ°ÑÐ°
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # ÐÐ²ÑÐ·Ð
    user = relationship("User")


class Transaction(Base):
    """ÐÐ¾Ð´ÐµÐ»Ñ ÑÑÐ°Ð½Ð·Ð°ÐºÑÐÐ (Ð¿Ð¾ÐºÑÐ¿ÐºÐ° Ð¿Ð¾ÐÐ½ÑÐ¾Ð²)"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # ÐÑÐ¼Ð¼Ð°
    amount = Column(Integer, nullable=False)  # ÐÐ¾Ð»ÐÑÐµÑÑÐ²Ð¾ Ð¿Ð¾ÐÐ½ÑÐ¾Ð²
    price = Column(Float, nullable=False)  # Ð¦ÐµÐ½Ð° Ð² ÑÑÐÐ»ÑÑ
    currency = Column(String, default="RUB")  # ÐÐ°Ð»ÑÑÐ° (RUB, USD, EUR, BTC, ETH Ð Ñ.Ð´.)
    
    # ÐÑÐ°ÑÑÑ
    status = Column(String, default="pending")  # pending, processing, completed, failed, refunded
    
    # ÐÐ»Ð°ÑÐµÐ¶Ð½Ð°Ñ ÑÐÑÑÐµÐ¼Ð°
    payment_provider = Column(String, nullable=False)  # telegram, stripe, yookassa, crypto, google_pay, samsung_pay
    payment_method = Column(String, nullable=True)  # card, crypto, wallet Ð Ñ.Ð´.
    payment_id = Column(String, nullable=True)  # ID Ð¿Ð»Ð°ÑÐµÐ¶Ð° Ð² Ð¿Ð»Ð°ÑÐµÐ¶Ð½Ð¾Ð¹ ÑÐÑÑÐµÐ¼Ðµ
    payment_url = Column(String, nullable=True)  # URL Ð´Ð»Ñ Ð¾Ð¿Ð»Ð°ÑÑ (Ð´Ð»Ñ ÐºÑÐÐ¿ÑÑ)
    
    # ÐÑÐÐ¿ÑÐ¾Ð²Ð°Ð»ÑÑÐ° (ÐµÑÐ»Ð ÐÑÐ¿Ð¾Ð»ÑÐ·ÑÐµÑÑÑ)
    crypto_currency = Column(String, nullable=True)  # BTC, ETH, USDT Ð Ñ.Ð´.
    crypto_address = Column(String, nullable=True)  # ÐÐ´ÑÐµÑ Ð´Ð»Ñ Ð¿Ð¾Ð»ÑÑÐµÐ½ÐÑ
    crypto_amount = Column(Float, nullable=True)  # ÐÑÐ¼Ð¼Ð° Ð² ÐºÑÐÐ¿ÑÐ¾Ð²Ð°Ð»ÑÑÐµ
    crypto_tx_hash = Column(String, nullable=True)  # ÐÐµÑ ÑÑÐ°Ð½Ð·Ð°ÐºÑÐÐ
    
    # ÐÑÐ¾Ð¼Ð¾ÐºÐ¾Ð´/ÑÐºÐÐ´ÐºÐ°
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id"), nullable=True)
    discount_amount = Column(Float, default=0.0)  # ÐÑÐ¼Ð¼Ð° ÑÐºÐÐ´ÐºÐ
    
    # ÐÐµÑÐ°Ð´Ð°Ð½Ð½ÑÐµ
    transaction_metadata = Column(Text, nullable=True)  # JSON Ñ Ð´Ð¾Ð¿Ð¾Ð»Ð½ÐÑÐµÐ»ÑÐ½ÑÐ¼Ð Ð´Ð°Ð½Ð½ÑÐ¼Ð
    
    # ÐÐ°ÑÑ
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # ÐÐ»Ñ ÐºÑÐÐ¿ÑÐ¾Ð¿Ð»Ð°ÑÐµÐ¶ÐµÐ¹
    
    # ÐÐ²ÑÐ·Ð
    user = relationship("User", back_populates="transactions")
    promo_code = relationship("PromoCode", back_populates="transactions")


class PromoCode(Base):
    """ÐÐ¾Ð´ÐµÐ»Ñ Ð¿ÑÐ¾Ð¼Ð¾ÐºÐ¾Ð´Ð°"""
    __tablename__ = "promo_codes"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    
    # Ð¢ÐÐ¿ ÑÐºÐÐ´ÐºÐ: percent (Ð¿ÑÐ¾ÑÐµÐ½Ñ) ÐÐ»Ð fixed (ÑÐÐºÑÐÑÐ¾Ð²Ð°Ð½Ð½Ð°Ñ ÑÑÐ¼Ð¼Ð°)
    discount_type = Column(String, nullable=False)  # percent, fixed
    discount_value = Column(Float, nullable=False)  # ÐÐ½Ð°ÑÐµÐ½ÐÐµ ÑÐºÐÐ´ÐºÐ
    
    # ÐÐÑÐ°Ð½ÐÑÐµÐ½ÐÑ
    max_uses = Column(Integer, nullable=True)  # ÐÐ°ÐºÑÐÐ¼Ð°Ð»ÑÐ½Ð¾Ðµ ÐºÐ¾Ð»ÐÑÐµÑÑÐ²Ð¾ ÐÑÐ¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°Ð½ÐÐ¹
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # ÐÑÐ¾Ðº Ð´ÐµÐ¹ÑÑÐ²ÐÑ
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    
    # ÐÐÐ½ÐÐ¼Ð°Ð»ÑÐ½Ð°Ñ ÑÑÐ¼Ð¼Ð° Ð·Ð°ÐºÐ°Ð·Ð°
    min_amount = Column(Float, nullable=True)
    
    # ÐÐ°ÑÑ
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)  # ID Ð°Ð´Ð¼ÐÐ½ÐÑÑÑÐ°ÑÐ¾ÑÐ°
    
    # ÐÐ²ÑÐ·Ð
    transactions = relationship("Transaction", back_populates="promo_code")


class PaymentMethod(Base):
    """ÐÐ¾Ð´ÐµÐ»Ñ Ð¿Ð»Ð°ÑÐµÐ¶Ð½Ð¾ÐÐ¾ Ð¼ÐµÑÐ¾Ð´Ð° Ð¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°ÑÐµÐ»Ñ"""
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Ð¢ÐÐ¿ Ð¼ÐµÑÐ¾Ð´Ð°
    method_type = Column(String, nullable=False)  # card, crypto, wallet
    provider = Column(String, nullable=False)  # telegram, stripe, yookassa, crypto
    
    # ÐÐ°Ð½Ð½ÑÐµ (Ð·Ð°ÑÐÑÑÐ¾Ð²Ð°Ð½Ð½ÑÐµ)
    encrypted_data = Column(Text, nullable=True)  # ÐÐ°ÑÐÑÑÐ¾Ð²Ð°Ð½Ð½ÑÐµ Ð´Ð°Ð½Ð½ÑÐµ ÐºÐ°ÑÑÑ/ÐºÐ¾ÑÐµÐ»ÑÐºÐ°
    last_four = Column(String, nullable=True)  # ÐÐ¾ÑÐ»ÐµÐ´Ð½ÐÐµ 4 ÑÐÑÑÑ ÐºÐ°ÑÑÑ
    
    # ÐÑÐÐ¿ÑÐ¾Ð²Ð°Ð»ÑÑÐ°
    crypto_currency = Column(String, nullable=True)
    crypto_address = Column(String, nullable=True)
    
    # ÐÑÐ°ÑÑÑ
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # ÐÐ°ÑÑ
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    
    # ÐÐ²ÑÐ·Ð
    user = relationship("User", back_populates="payment_methods")


class Withdrawal(Base):
    """ÐÐ¾Ð´ÐµÐ»Ñ Ð²ÑÐ²Ð¾Ð´Ð° ÑÑÐµÐ´ÑÑÐ²"""
    __tablename__ = "withdrawals"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # ÐÑÐ¼Ð¼Ð°
    amount = Column(Float, nullable=False)  # ÐÑÐ¼Ð¼Ð° Ð² ÑÑÐÐ»ÑÑ
    currency = Column(String, default="RUB")
    
    # ÐÐµÑÐ¾Ð´ Ð²ÑÐ²Ð¾Ð´Ð°
    withdrawal_method = Column(String, nullable=False)  # card, crypto, wallet
    withdrawal_details = Column(Text, nullable=True)  # JSON Ñ Ð´ÐµÑÐ°Ð»ÑÐ¼Ð
    
    # ÐÑÐ°ÑÑÑ
    status = Column(String, default="pending")  # pending, processing, completed, rejected, cancelled
    
    # ÐÐ¾Ð¼ÐÑÑÐÑ
    fee = Column(Float, default=0.0)
    net_amount = Column(Float, nullable=False)  # ÐÑÐ¼Ð¼Ð° Ð¿Ð¾ÑÐ»Ðµ ÐºÐ¾Ð¼ÐÑÑÐÐ
    
    # ÐÐ¾Ð´ÐµÑÐ°ÑÐÑ
    admin_notes = Column(Text, nullable=True)
    processed_by = Column(Integer, nullable=True)  # ID Ð°Ð´Ð¼ÐÐ½ÐÑÑÑÐ°ÑÐ¾ÑÐ°
    
    # ÐÐ°ÑÑ
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # ÐÐ²ÑÐ·Ð
    user = relationship("User", back_populates="withdrawals")

