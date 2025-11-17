"""Схемы данных API"""
from pydantic import BaseModel
from typing import Optional


class GenerateImageRequest(BaseModel):
    """Запрос на генерацию изображения"""
    telegram_id: int
    prompt: str
    model: Optional[str] = "flux"
    style: Optional[str] = None
    negative_prompt: Optional[str] = None
    width: int = 1024
    height: int = 1024


class GenerateImageResponse(BaseModel):
    """Ответ на генерацию изображения"""
    success: bool
    message: str
    image_url: Optional[str] = None
    generation_id: Optional[int] = None


class SwapFaceResponse(BaseModel):
    """Ответ на замену лица"""
    success: bool
    message: str
    video_url: Optional[str] = None
    generation_id: Optional[int] = None


class UserResponse(BaseModel):
    """Информация о пользователе"""
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    balance: int
    free_generations: int
    total_generations: int
    total_deepfakes: int
    is_premium: bool
    referral_code: Optional[str] = None


class RegisterRequest(BaseModel):
    """Запрос на регистрацию"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    referral_code: Optional[str] = None


class RegisterResponse(BaseModel):
    """Ответ на регистрацию"""
    success: bool
    message: str
    user: Optional[UserResponse] = None


class LoginRequest(BaseModel):
    """Запрос на вход"""
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None


class LoginResponse(BaseModel):
    """Ответ на вход"""
    success: bool
    message: str
    user: Optional[UserResponse] = None


class LogoutResponse(BaseModel):
    """Ответ на выход"""
    success: bool
    message: str


class GenerateVideoRequest(BaseModel):
    """Запрос на генерацию видео"""
    telegram_id: int
    prompt: str
    model: Optional[str] = "runway"
    style: Optional[str] = None
    negative_prompt: Optional[str] = None
    duration: int = 5
    fps: int = 24
    width: int = 1280
    height: int = 720


class GenerateVideoResponse(BaseModel):
    """Ответ на генерацию видео"""
    success: bool
    message: str
    video_url: Optional[str] = None
    task_id: Optional[str] = None
    generation_id: Optional[int] = None


class StatsResponse(BaseModel):
    """Статистика системы"""
    total_users: int
    total_generations: int
    total_deepfakes: int
    active_users_today: int

