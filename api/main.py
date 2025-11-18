"""Главный файл FastAPI приложения"""
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
from datetime import datetime
import logging
import uuid
import os
import io
import qrcode

from database import get_session, User, Generation
from services import deepface_service, image_generation_service, video_generation_service, user_service, content_moderation, background_removal_service
from config import settings
from api.schemas import (
    GenerateImageRequest,
    GenerateImageResponse,
    GenerateVideoRequest,
    GenerateVideoResponse,
    SwapFaceResponse,
    UserResponse,
    StatsResponse,
    ActivatePlanResponse
)

# Импорт платежного модуля (опционально)
try:
    from api import payments
except ImportError:
    payments = None

logger = logging.getLogger(__name__)

# Создаем приложение FastAPI
app = FastAPI(
    title="DeepFace API",
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

# Монтируем статические файлы (с обработкой ошибок для serverless)
BASE_DIR = Path(__file__).resolve().parent.parent

# Создаем директории если их нет (для serverless)
static_dir = BASE_DIR / "static"
uploads_dir = BASE_DIR / "uploads"
generated_dir = BASE_DIR / "generated"

static_dir.mkdir(exist_ok=True)
uploads_dir.mkdir(exist_ok=True)
generated_dir.mkdir(exist_ok=True)

# Монтируем только если директории существуют
if static_dir.exists():
    try:
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    except Exception as e:
        logger.warning(f"Could not mount static directory: {e}")

if uploads_dir.exists():
    try:
        app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
    except Exception as e:
        logger.warning(f"Could not mount uploads directory: {e}")

if generated_dir.exists():
    try:
        app.mount("/generated", StaticFiles(directory=str(generated_dir)), name="generated")
    except Exception as e:
        logger.warning(f"Could not mount generated directory: {e}")

# Подключаем роутеры
if payments:
    app.include_router(payments.router)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Главная страница - Web App"""
    template_path = BASE_DIR / "templates" / "index.html"
    
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            
            # Вставляем ссылку на оплату в JavaScript
            payment_url = settings.STANDARD_PLAN_PAYMENT_URL or "https://web.tribute.tg/p/n1Q"
            logger.info(f"Setting STANDARD_PLAN_PAYMENT_URL to: {payment_url}")
            # Экранируем кавычки в URL для безопасности
            payment_url_escaped = payment_url.replace('"', '\\"').replace("'", "\\'")
            script_injection = f"""
            <script>
                window.STANDARD_PLAN_PAYMENT_URL = "{payment_url_escaped}";
                console.log('STANDARD_PLAN_PAYMENT_URL set to:', window.STANDARD_PLAN_PAYMENT_URL);
            </script>
            """
            # Вставляем скрипт перед закрывающим тегом head
            html_content = html_content.replace("</head>", script_injection + "</head>")
            
            return HTMLResponse(content=html_content)
    
    return HTMLResponse(content="<h1>Web App</h1><p>Template not found</p>")


@app.get("/api/user/{telegram_id}", response_model=UserResponse)
async def get_user(
    telegram_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Получить информацию о пользователе"""
    # Всегда используем get_or_create_user чтобы гарантировать создание referral_code
    user = await user_service.get_or_create_user(
        session,
        telegram_id=telegram_id
    )
    
    # Убеждаемся, что referral_code всегда есть
    if not user.referral_code:
        logger.warning(f"User {telegram_id} has no referral_code, generating one...")
        new_referral_code = user_service.generate_referral_code()
        # Проверяем уникальность
        while True:
            check_result = await session.execute(
                select(User).where(User.referral_code == new_referral_code)
            )
            if check_result.scalar_one_or_none() is None:
                break
            new_referral_code = user_service.generate_referral_code()
        user.referral_code = new_referral_code
        await session.commit()
        await session.refresh(user)
        logger.info(f"Generated referral_code {new_referral_code} for user {telegram_id}")
    
    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        balance=user.balance,
        free_generations=user.free_generations,
        total_generations=user.total_generations,
        total_deepfakes=user.total_deepfakes,
        is_premium=user.is_premium,
        plan_type=getattr(user, 'plan_type', 'basic'),
        images_used=getattr(user, 'images_used', 0),
        videos_used=getattr(user, 'videos_used', 0),
        referral_code=user.referral_code
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
            detail=f"Запрос отклонен: {reason}\n\n"
                   "Пожалуйста, ознакомьтесь с политикой контента (/help в боте)."
        )
    
    # Получаем или создаем пользователя автоматически
    user = await user_service.get_or_create_user(
        session,
        telegram_id=request.telegram_id
    )
    
    # Проверка ограничений тарифа
    plan_type = getattr(user, 'plan_type', 'basic')
    if plan_type == 'basic':
        images_used = getattr(user, 'images_used', 0)
        if images_used >= 5:
            raise HTTPException(
                status_code=403,
                detail="Достигнут лимит базового тарифа: максимум 5 изображений. Обновите тариф до Стандарт для неограниченного использования."
            )
    
    # Создаем запись о генерации
    generation = Generation(
        user_id=user.id,
        generation_type="image",
        prompt=request.prompt,
        model=request.model,
        style=request.style,
        cost=0,
        status="processing"
    )
    session.add(generation)
    await session.commit()
    
    try:
        logger.info(f"Starting image generation for user {user.telegram_id}, prompt: {request.prompt[:50]}...")
        
        # Генерируем изображение
        result = await image_generation_service.generate_image(
            prompt=request.prompt,
            model=request.model or "flux",
            style=request.style
        )
        
        logger.info(f"Image generation result: status={result.get('status')}, has_images={bool(result.get('images'))}")
        
        if result.get("status") == "success":
            image_url = result.get("images", [""])[0]
            if not image_url:
                logger.error("No image URL in successful response")
                generation.status = "failed"
                generation.error_message = "No image URL received"
                await session.commit()
                raise HTTPException(status_code=500, detail="No image URL received from generation service")
            
            # Обновляем статистику и счетчики тарифа
            user.total_generations += 1
            plan_type = getattr(user, 'plan_type', 'basic')
            if plan_type == 'basic':
                user.images_used = getattr(user, 'images_used', 0) + 1
            generation.status = "completed"
            generation.result_file = image_url
            
            await session.commit()
            
            logger.info(f"Image generation completed successfully, URL: {image_url}")
            
            return GenerateImageResponse(
                success=True,
                message="Image generated successfully",
                image_url=image_url,
                generation_id=generation.id
            )
        else:
            error_msg = result.get("message", "Unknown error")
            logger.error(f"Image generation failed: {error_msg}")
            generation.status = "failed"
            generation.error_message = error_msg
            await session.commit()
            
            raise HTTPException(status_code=500, detail=error_msg)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating image: {e}", exc_info=True)
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
    # Получаем или создаем пользователя автоматически
    user = await user_service.get_or_create_user(
        session,
        telegram_id=telegram_id
    )
    
    # Проверка ограничений тарифа для Face Swap (считается как видео)
    plan_type = getattr(user, 'plan_type', 'basic')
    if plan_type == 'basic':
        videos_used = getattr(user, 'videos_used', 0)
        if videos_used >= 2:
            raise HTTPException(
                status_code=403,
                detail="Достигнут лимит базового тарифа: максимум 2 видео. Обновите тариф до Стандарт для неограниченного использования."
            )
    
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
        
        # Создаем запись о генерации (без проверки баланса - бесплатный доступ)
        generation = Generation(
            user_id=user.id,
            generation_type="deepfake",
            source_file=str(source_path),
            target_file=str(target_path),
            cost=0,  # Бесплатно
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
            # Обновляем статистику и счетчики тарифа
            user.total_deepfakes += 1
            plan_type = getattr(user, 'plan_type', 'basic')
            if plan_type == 'basic':
                user.videos_used = getattr(user, 'videos_used', 0) + 1
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


@app.get("/api/deepfake/task/{task_id}")
async def check_deepfake_task_status(task_id: str):
    """Проверить статус задачи смены лица"""
    try:
        result = await deepface_service.check_task_status(task_id)
        return result
    except Exception as e:
        logger.error(f"Error checking deepfake task status: {e}")
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


@app.post("/api/generate/video", response_model=GenerateVideoResponse)
async def generate_video(
    request: GenerateVideoRequest,
    session: AsyncSession = Depends(get_session)
):
    """Генерация видео по текстовому описанию"""
    # Проверка контента на допустимость
    is_allowed, reason = content_moderation.check_text_content(request.prompt)
    if not is_allowed:
        content_moderation.log_violation(
            request.telegram_id,
            "video_generation",
            request.prompt,
            reason
        )
        raise HTTPException(
            status_code=400,
            detail=f"Запрос отклонен: {reason}\n\n"
                   "Пожалуйста, ознакомьтесь с политикой контента (/help в боте)."
        )
    
    # Получаем или создаем пользователя автоматически
    user = await user_service.get_or_create_user(
        session,
        telegram_id=request.telegram_id
    )
    
    # Проверка ограничений тарифа
    plan_type = getattr(user, 'plan_type', 'basic')
    if plan_type == 'basic':
        videos_used = getattr(user, 'videos_used', 0)
        if videos_used >= 2:
            raise HTTPException(
                status_code=403,
                detail="Достигнут лимит базового тарифа: максимум 2 видео. Обновите тариф до Стандарт для неограниченного использования."
            )
    
    # Создаем запись о генерации
    generation = Generation(
        user_id=user.id,
        generation_type="video",
        prompt=request.prompt,
        model=request.model,
        style=request.style,
        cost=0,
        status="processing"
    )
    session.add(generation)
    await session.commit()
    
    try:
        # Генерируем видео (используем экземпляр сервиса)
        result = await video_generation_service.generate_video(
            prompt=request.prompt,
            model=request.model or "sora",
            style=request.style,
            negative_prompt=request.negative_prompt,
            duration=request.duration,
            fps=request.fps,
            width=request.width,
            height=request.height
        )
        
        if result["status"] == "success":
            # Обновляем статистику и счетчики тарифа
            user.total_generations += 1
            plan_type = getattr(user, 'plan_type', 'basic')
            if plan_type == 'basic':
                user.videos_used = getattr(user, 'videos_used', 0) + 1
            generation.status = "completed"
            generation.result_file = result.get("video_url") or result.get("video")
            
            # Если есть task_id, сохраняем его для отслеживания статуса
            if result.get("task_id"):
                generation.error_message = f"task_id:{result['task_id']}"  # Временно используем это поле
            
            await session.commit()
            
            return GenerateVideoResponse(
                success=True,
                message="Video generation started successfully",
                video_url=result.get("video_url") or result.get("video"),
                task_id=result.get("task_id"),
                generation_id=generation.id
            )
        else:
            generation.status = "failed"
            generation.error_message = result.get("message", "Unknown error")
            await session.commit()
            
            raise HTTPException(status_code=500, detail=result.get("message", "Video generation failed"))
    
    except Exception as e:
        logger.error(f"Error generating video: {e}")
        generation.status = "failed"
        generation.error_message = str(e)
        await session.commit()
        
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/video/task/{task_id}")
async def check_video_task_status(task_id: str):
    """Проверить статус задачи генерации видео"""
    try:
        result = await video_generation_service.check_video_task_status(task_id)
        return result
    except Exception as e:
        logger.error(f"Error checking video task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/video/models")
async def get_video_models():
    """Получить список доступных моделей для генерации видео"""
    models = await video_generation_service.get_available_video_models()
    return {"models": models}


@app.get("/api/video/styles")
async def get_video_styles():
    """Получить список доступных стилей для видео"""
    styles = await video_generation_service.get_available_video_styles()
    return {"styles": styles}


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(
    session: AsyncSession = Depends(get_session)
):
    """Получить статистику системы"""
    try:
        stats = await user_service.get_stats(session)
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/user/{telegram_id}/activate-basic-plan", response_model=ActivatePlanResponse)
async def activate_basic_plan(
    telegram_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Активация базового тарифа (бесплатный)"""
    user = await user_service.get_user_by_telegram_id(session, telegram_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Активируем базовый тариф
    user.plan_type = "basic"
    user.plan_activated_at = datetime.utcnow()
    user.images_used = 0
    user.videos_used = 0
    
    await session.commit()
    
    logger.info(f"Activated basic plan for user {telegram_id}")
    
    return ActivatePlanResponse(
        success=True,
        message="Базовый тариф успешно активирован!",
        plan_type="basic"
    )


@app.get("/api/referral/qr")
async def generate_referral_qr(
    telegram_id: int = Query(..., description="Telegram ID пользователя"),
    session: AsyncSession = Depends(get_session)
):
    """Генерация QR-кода для реферальной ссылки"""
    try:
        # Получаем пользователя
        user = await user_service.get_user_by_telegram_id(session, telegram_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Получаем реферальный код
        referral_code = user.referral_code
        if not referral_code:
            raise HTTPException(status_code=400, detail="Referral code not found")
        
        # Формируем реферальную ссылку
        webapp_url = settings.WEBAPP_URL or "https://facy-app.vercel.app"
        referral_link = f"{webapp_url}?ref={referral_code}"
        
        # Генерируем QR-код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(referral_link)
        qr.make(fit=True)
        
        # Создаем изображение
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Конвертируем в bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return Response(
            content=img_byte_arr.getvalue(),
            media_type="image/png",
            headers={
                "Cache-Control": "public, max-age=3600"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/remove-background")
async def remove_background(
    image: UploadFile = File(...),
    threshold: int = Query(240, ge=0, le=255, description="Порог для определения белого цвета")
):
    """Удалить белый фон из изображения"""
    try:
        # Читаем изображение
        image_bytes = await image.read()
        
        # Удаляем фон
        processed_bytes = background_removal_service.remove_white_background(
            image_bytes,
            threshold
        )
        
        return Response(
            content=processed_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=no-background-{image.filename or 'image.png'}"
            }
        )
    except Exception as e:
        logger.error(f"Error removing background: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy"}

