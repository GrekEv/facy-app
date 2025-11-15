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

