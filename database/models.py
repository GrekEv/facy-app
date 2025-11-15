"""Модели базы данных"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


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
    
    # Статистика
    total_generations = Column(Integer, default=0)
    total_deepfakes = Column(Integer, default=0)
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    generations = relationship("Generation", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


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
    
    # Связи
    user = relationship("User", back_populates="generations")


class Transaction(Base):
    """Модель транзакции (покупка поинтов)"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Сумма
    amount = Column(Integer, nullable=False)  # Количество поинтов
    price = Column(Float, nullable=False)  # Цена в рублях
    
    # Статус
    status = Column(String, default="pending")  # pending, completed, failed
    
    # Платежная система
    payment_provider = Column(String, nullable=True)
    payment_id = Column(String, nullable=True)
    
    # Даты
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="transactions")

