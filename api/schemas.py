"""��ем� данн�� API"""
from pydantic import BaseModel
from typing import Optional


class GenerateImageRequest(BaseModel):
    """Зап�о� на �ене�ац�� �зо��ажен��"""
    telegram_id: int
    prompt: str
    model: Optional[str] = "flux"
    style: Optional[str] = None
    negative_prompt: Optional[str] = None
    width: int = 1024
    height: int = 1024


class GenerateImageResponse(BaseModel):
    """Ответ на �ене�ац�� �зо��ажен��"""
    success: bool
    message: str
    image_url: Optional[str] = None
    generation_id: Optional[int] = None


class SwapFaceResponse(BaseModel):
    """Ответ на замену л�ца"""
    success: bool
    message: str
    video_url: Optional[str] = None
    generation_id: Optional[int] = None


class UserResponse(BaseModel):
    """Инфо�мац�� о пол�зователе"""
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
    """Ответ на акт�вац�� та��фа"""
    success: bool
    message: str
    plan_type: Optional[str] = None


class RegisterRequest(BaseModel):
    """Зап�о� на �е���т�ац��"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    referral_code: Optional[str] = None


class RegisterResponse(BaseModel):
    """Ответ на �е���т�ац��"""
    success: bool
    message: str
    user: Optional[UserResponse] = None


class LoginRequest(BaseModel):
    """Зап�о� на в�од"""
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None


class LoginResponse(BaseModel):
    """Ответ на в�од"""
    success: bool
    message: str
    user: Optional[UserResponse] = None


class LogoutResponse(BaseModel):
    """Ответ на в��од"""
    success: bool
    message: str


class GenerateVideoRequest(BaseModel):
    """Зап�о� на �ене�ац�� в�део"""
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
    """Ответ на �ене�ац�� в�део"""
    success: bool
    message: str
    video_url: Optional[str] = None
    task_id: Optional[str] = None
    generation_id: Optional[int] = None


class StatsResponse(BaseModel):
    """�тат��т�ка ���тем�"""
    total_users: int
    total_generations: int
    total_deepfakes: int
    active_users_today: int


class SendVerificationCodeRequest(BaseModel):
    """Зап�о� на отп�авку кода подтве�жден��"""
    telegram_id: int
    email: str


class SendVerificationCodeResponse(BaseModel):
    """Ответ на отп�авку кода подтве�жден��"""
    success: bool
    message: str


class VerifyEmailCodeRequest(BaseModel):
    """Зап�о� на п�ове�ку кода подтве�жден��"""
    telegram_id: int
    code: str


class VerifyEmailCodeResponse(BaseModel):
    """Ответ на п�ове�ку кода подтве�жден��"""
    success: bool
    message: str
    email_verified: bool = False

