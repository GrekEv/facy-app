"""ÐÑÐµÐ¼Ñ Ð´Ð°Ð½Ð½ÑÑ API"""
from pydantic import BaseModel
from typing import Optional


class GenerateImageRequest(BaseModel):
    """ÐÐ°Ð¿ÑÐ¾Ñ Ð½Ð° ÐÐµÐ½ÐµÑÐ°ÑÐÑ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ"""
    telegram_id: int
    prompt: str
    model: Optional[str] = "flux"
    style: Optional[str] = None
    negative_prompt: Optional[str] = None
    width: int = 1024
    height: int = 1024


class GenerateImageResponse(BaseModel):
    """ÐÑÐ²ÐµÑ Ð½Ð° ÐÐµÐ½ÐµÑÐ°ÑÐÑ ÐÐ·Ð¾ÐÑÐ°Ð¶ÐµÐ½ÐÑ"""
    success: bool
    message: str
    image_url: Optional[str] = None
    generation_id: Optional[int] = None


class SwapFaceResponse(BaseModel):
    """ÐÑÐ²ÐµÑ Ð½Ð° Ð·Ð°Ð¼ÐµÐ½Ñ Ð»ÐÑÐ°"""
    success: bool
    message: str
    video_url: Optional[str] = None
    generation_id: Optional[int] = None


class UserResponse(BaseModel):
    """ÐÐ½ÑÐ¾ÑÐ¼Ð°ÑÐÑ Ð¾ Ð¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°ÑÐµÐ»Ðµ"""
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    balance: int
    free_generations: int
    total_generations: int
    total_deepfakes: int
    is_premium: bool
    plan_type: Optional[str] = "basic"
    images_used: Optional[int] = 0
    videos_used: Optional[int] = 0
    referral_code: Optional[str] = None
    email: Optional[str] = None
    email_verified: bool = False


class ActivatePlanResponse(BaseModel):
    """ÐÑÐ²ÐµÑ Ð½Ð° Ð°ÐºÑÐÐ²Ð°ÑÐÑ ÑÐ°ÑÐÑÐ°"""
    success: bool
    message: str
    plan_type: Optional[str] = None


class RegisterRequest(BaseModel):
    """ÐÐ°Ð¿ÑÐ¾Ñ Ð½Ð° ÑÐµÐÐÑÑÑÐ°ÑÐÑ"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    referral_code: Optional[str] = None


class RegisterResponse(BaseModel):
    """ÐÑÐ²ÐµÑ Ð½Ð° ÑÐµÐÐÑÑÑÐ°ÑÐÑ"""
    success: bool
    message: str
    user: Optional[UserResponse] = None


class LoginRequest(BaseModel):
    """ÐÐ°Ð¿ÑÐ¾Ñ Ð½Ð° Ð²ÑÐ¾Ð´"""
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None


class LoginResponse(BaseModel):
    """ÐÑÐ²ÐµÑ Ð½Ð° Ð²ÑÐ¾Ð´"""
    success: bool
    message: str
    user: Optional[UserResponse] = None


class LogoutResponse(BaseModel):
    """ÐÑÐ²ÐµÑ Ð½Ð° Ð²ÑÑÐ¾Ð´"""
    success: bool
    message: str


class GenerateVideoRequest(BaseModel):
    """ÐÐ°Ð¿ÑÐ¾Ñ Ð½Ð° ÐÐµÐ½ÐµÑÐ°ÑÐÑ Ð²ÐÐ´ÐµÐ¾"""
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
    """ÐÑÐ²ÐµÑ Ð½Ð° ÐÐµÐ½ÐµÑÐ°ÑÐÑ Ð²ÐÐ´ÐµÐ¾"""
    success: bool
    message: str
    video_url: Optional[str] = None
    task_id: Optional[str] = None
    generation_id: Optional[int] = None


class StatsResponse(BaseModel):
    """ÐÑÐ°ÑÐÑÑÐÐºÐ° ÑÐÑÑÐµÐ¼Ñ"""
    total_users: int
    total_generations: int
    total_deepfakes: int
    active_users_today: int


class SendVerificationCodeRequest(BaseModel):
    """ÐÐ°Ð¿ÑÐ¾Ñ Ð½Ð° Ð¾ÑÐ¿ÑÐ°Ð²ÐºÑ ÐºÐ¾Ð´Ð° Ð¿Ð¾Ð´ÑÐ²ÐµÑÐ¶Ð´ÐµÐ½ÐÑ"""
    telegram_id: int
    email: str


class SendVerificationCodeResponse(BaseModel):
    """ÐÑÐ²ÐµÑ Ð½Ð° Ð¾ÑÐ¿ÑÐ°Ð²ÐºÑ ÐºÐ¾Ð´Ð° Ð¿Ð¾Ð´ÑÐ²ÐµÑÐ¶Ð´ÐµÐ½ÐÑ"""
    success: bool
    message: str


class VerifyEmailCodeRequest(BaseModel):
    """ÐÐ°Ð¿ÑÐ¾Ñ Ð½Ð° Ð¿ÑÐ¾Ð²ÐµÑÐºÑ ÐºÐ¾Ð´Ð° Ð¿Ð¾Ð´ÑÐ²ÐµÑÐ¶Ð´ÐµÐ½ÐÑ"""
    telegram_id: int
    code: str


class VerifyEmailCodeResponse(BaseModel):
    """ÐÑÐ²ÐµÑ Ð½Ð° Ð¿ÑÐ¾Ð²ÐµÑÐºÑ ÐºÐ¾Ð´Ð° Ð¿Ð¾Ð´ÑÐ²ÐµÑÐ¶Ð´ÐµÐ½ÐÑ"""
    success: bool
    message: str
    email_verified: bool = False

