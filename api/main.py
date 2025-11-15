"""Главный файл FastAPI приложения"""
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import logging
import uuid
import os

from database import get_session, User, Generation
from services import deepface_service, image_generation_service, user_service, content_moderation
from .schemas import (
    GenerateImageRequest,
    GenerateImageResponse,
    SwapFaceResponse,
    UserResponse
)

logger = logging.getLogger(__name__)

# Создаем приложение FastAPI
app = FastAPI(
    title="DeepFace AI API",
    description="API для замены лиц и генерации изображений",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем статические файлы
BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/uploads", StaticFiles(directory=str(BASE_DIR / "uploads")), name="uploads")
app.mount("/generated", StaticFiles(directory=str(BASE_DIR / "generated")), name="generated")

# Подключаем роутеры
if payments:
    app.include_router(payments.router)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница - Web App"""
    template_path = BASE_DIR / "templates" / "index.html"
    
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    
    return HTMLResponse(content="<h1>Web App</h1><p>Template not found</p>")


@app.get("/api/user/{telegram_id}", response_model=UserResponse)
async def get_user(
    telegram_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Получить информацию о пользователе"""
    user = await user_service.get_user_by_telegram_id(session, telegram_id)
    
    if not user:
        # Создаем пользователя если не существует
        user = await user_service.get_or_create_user(
            session,
            telegram_id=telegram_id
        )
    
    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        balance=user.balance,
        free_generations=user.free_generations,
        total_generations=user.total_generations,
        total_deepfakes=user.total_deepfakes,
        is_premium=user.is_premium
    )


@app.post("/api/generate/image", response_model=GenerateImageResponse)
async def generate_image(
    request: GenerateImageRequest,
    session: AsyncSession = Depends(get_session)
):
    """Генерация изображения"""
    # Проверка контента на допустимость
    is_allowed, reason = content_moderation.check_text_content(request.prompt)
    if not is_allowed:
        content_moderation.log_violation(
            request.telegram_id,
            "image_generation",
            request.prompt,
            reason
        )
        raise HTTPException(
            status_code=400,
            detail=f"❌ Запрос отклонен: {reason}\n\n"
                   "Пожалуйста, ознакомьтесь с политикой контента (/help в боте)."
        )
    
    # Получаем пользователя
    user = await user_service.get_user_by_telegram_id(session, request.telegram_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем баланс
    cost = 10
    if not await user_service.can_afford(user, cost):
        raise HTTPException(status_code=402, detail="Insufficient balance")
    
    # Создаем запись о генерации
    generation = Generation(
        user_id=user.id,
        generation_type="image",
        prompt=request.prompt,
        model=request.model,
        style=request.style,
        cost=cost,
        status="processing"
    )
    session.add(generation)
    await session.commit()
    
    try:
        # Генерируем изображение
        result = await image_generation_service.generate_image(
            prompt=request.prompt,
            model=request.model or "flux",
            style=request.style
        )
        
        if result["status"] == "success":
            # Списываем средства
            if user.free_generations > 0:
                user.free_generations -= 1
            else:
                await user_service.update_balance(session, user, -cost)
            
            user.total_generations += 1
            generation.status = "completed"
            generation.result_file = result.get("images", [""])[0]
            
            await session.commit()
            
            return GenerateImageResponse(
                success=True,
                message="Image generated successfully",
                image_url=result.get("images", [""])[0],
                generation_id=generation.id
            )
        else:
            generation.status = "failed"
            generation.error_message = result.get("message", "Unknown error")
            await session.commit()
            
            raise HTTPException(status_code=500, detail=result.get("message", "Generation failed"))
    
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        generation.status = "failed"
        generation.error_message = str(e)
        await session.commit()
        
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/deepfake/swap", response_model=SwapFaceResponse)
async def swap_face(
    telegram_id: int = Form(...),
    source_image: UploadFile = File(...),
    target_video: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
):
    """Замена лица в видео"""
    # Получаем пользователя
    user = await user_service.get_user_by_telegram_id(session, telegram_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем баланс
    cost = 50
    if not await user_service.can_afford(user, cost):
        raise HTTPException(status_code=402, detail="Insufficient balance")
    
    try:
        # Сохраняем загруженные файлы
        uploads_dir = BASE_DIR / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        
        source_path = uploads_dir / f"{uuid.uuid4()}_{source_image.filename}"
        target_path = uploads_dir / f"{uuid.uuid4()}_{target_video.filename}"
        
        with open(source_path, "wb") as f:
            f.write(await source_image.read())
        
        with open(target_path, "wb") as f:
            f.write(await target_video.read())
        
        # Создаем запись о генерации
        generation = Generation(
            user_id=user.id,
            generation_type="deepfake",
            source_file=str(source_path),
            target_file=str(target_path),
            cost=cost,
            status="processing"
        )
        session.add(generation)
        await session.commit()
        
        # Обрабатываем видео
        output_dir = BASE_DIR / "generated"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{uuid.uuid4()}_result.mp4"
        
        result = await deepface_service.swap_face(
            str(source_path),
            str(target_path),
            str(output_path)
        )
        
        if result["status"] == "success":
            # Списываем средства
            if user.free_generations > 0:
                user.free_generations -= 1
            else:
                await user_service.update_balance(session, user, -cost)
            
            user.total_deepfakes += 1
            generation.status = "completed"
            generation.result_file = str(output_path)
            
            await session.commit()
            
            return SwapFaceResponse(
                success=True,
                message="Face swap completed successfully",
                video_url=f"/generated/{output_path.name}",
                generation_id=generation.id
            )
        else:
            generation.status = "failed"
            generation.error_message = result.get("message", "Unknown error")
            await session.commit()
            
            raise HTTPException(status_code=500, detail=result.get("message", "Face swap failed"))
    
    except Exception as e:
        logger.error(f"Error in face swap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def get_models():
    """Получить список доступных моделей"""
    models = await image_generation_service.get_available_models()
    return {"models": models}


@app.get("/api/styles")
async def get_styles():
    """Получить список доступных стилей"""
    styles = await image_generation_service.get_available_styles()
    return {"styles": styles}


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy"}

