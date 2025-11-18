from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
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
    ActivatePlanResponse,
    SendVerificationCodeRequest,
    SendVerificationCodeResponse,
    VerifyEmailCodeRequest,
    VerifyEmailCodeResponse
)
try:
    from api import payments
except ImportError:
    payments = None
logger = logging.getLogger(__name__)
app = FastAPI(
    title="DeepFace API",
    description="API дл� замен� л�ц � �ене�ац�� �зо��ажен�й",
    version="1.0.0"
)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
BASE_DIR = Path(__file__).resolve().parent.parent
static_dir = BASE_DIR / "static"
static_images_dir = static_dir / "images"
uploads_dir = BASE_DIR / "uploads"
generated_dir = BASE_DIR / "generated"
static_dir.mkdir(exist_ok=True)
static_images_dir.mkdir(exist_ok=True)
uploads_dir.mkdir(exist_ok=True)
generated_dir.mkdir(exist_ok=True)
if static_dir.exists():
    try:
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        logger.info(f"Static files mounted from: {static_dir.absolute()}")
        if static_images_dir.exists():
            images = list(static_images_dir.glob("*.png")) + list(static_images_dir.glob("*.jpg"))
            logger.info(f"Found {len(images)} images in static/images/")
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
if payments:
    app.include_router(payments.router)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    env_log_file = BASE_DIR / "env_check.log"
    env_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_url": str(request.url),
        "request_method": request.method,
        "headers": dict(request.headers),
        "os_getenv": {
            "API_BASE_URL": os.getenv("API_BASE_URL", "NOT SET"),
            "WEBAPP_URL": os.getenv("WEBAPP_URL", "NOT SET"),
            "DATABASE_URL": "SET" if os.getenv("DATABASE_URL") else "NOT SET",
            "BOT_TOKEN": "SET" if os.getenv("BOT_TOKEN") else "NOT SET",
            "REPLICATE_API_KEY": "SET" if os.getenv("REPLICATE_API_KEY") else "NOT SET",
        },
        "settings": {
            "WEBAPP_URL": settings.WEBAPP_URL or "NOT SET",
            "DATABASE_URL": "SET" if settings.DATABASE_URL else "NOT SET",
            "BOT_TOKEN": "SET" if settings.BOT_TOKEN else "NOT SET",
        }
    }
    
    try:
        with open(env_log_file, "a", encoding="utf-8") as log_f:
            import json
            log_f.write(json.dumps(env_info, indent=2, ensure_ascii=False) + "\n" + "="*80 + "\n")
        logger.info(f"Environment info logged to {env_log_file}")
    except Exception as e:
        logger.error(f"Failed to write env log: {e}")
    
    print("\n" + "="*80)
    print("ENVIRONMENT VARIABLES CHECK")
    print("="*80)
    print(f"\nTimestamp: {env_info['timestamp']}")
    print(f"Request URL: {env_info['request_url']}")
    print(f"Request Method: {env_info['request_method']}")
    print("\n--- os.getenv values ---")
    for key, value in env_info['os_getenv'].items():
        if 'TOKEN' in key or 'KEY' in key or 'PASSWORD' in key:
            print(f"  {key}: {'SET' if value and value != 'NOT SET' else 'NOT SET'}")
        else:
            print(f"  {key}: {value}")
    print("\n--- settings values ---")
    for key, value in env_info['settings'].items():
        if 'TOKEN' in key or 'KEY' in key or 'PASSWORD' in key or 'DATABASE_URL' in key:
            print(f"  {key}: {'SET' if value and value != 'NOT SET' else 'NOT SET'}")
        else:
            print(f"  {key}: {value}")
    print("="*80 + "\n")
    
    template_path = BASE_DIR / "templates" / "index.html"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            api_base_url = os.getenv("API_BASE_URL", "")
            webapp_url = settings.WEBAPP_URL or ""
            if not api_base_url:
                api_base_url = ""
            logger.info(f"Injecting API_BASE_URL: '{api_base_url}', WEBAPP_URL: '{webapp_url}'")
            html_content = html_content.replace("{{API_BASE_URL}}", api_base_url)
            html_content = html_content.replace("{{WEBAPP_URL}}", webapp_url)
            payment_url = settings.STANDARD_PLAN_PAYMENT_URL or "https://web.tribute.tg/p/n1Q"
            logger.info(f"Setting STANDARD_PLAN_PAYMENT_URL to: {payment_url}")
            payment_url_escaped = payment_url.replace('"', '\\"').replace("'", "\\'")
            script_injection = f"""
            <script>
                window.STANDARD_PLAN_PAYMENT_URL = "{payment_url_escaped}";
                console.log('STANDARD_PLAN_PAYMENT_URL set to:', window.STANDARD_PLAN_PAYMENT_URL);
            </script>
            """
            html_content = html_content.replace("</head>", script_injection + "</head>")
            return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Web App</h1><p>Template not found</p>")
@app.get("/api/user/{telegram_id}", response_model=UserResponse)
async def get_user(
    telegram_id: int,
    session: AsyncSession = Depends(get_session)
):
    try:
        user = await user_service.get_or_create_user(
            session,
            telegram_id=telegram_id
        )
        if not user.referral_code:
            logger.warning(f"User {telegram_id} has no referral_code, generating one...")
            new_referral_code = user_service.generate_referral_code()
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
            referral_code=user.referral_code,
            email=getattr(user, 'email', None),
            email_verified=getattr(user, 'email_verified', False)
        )
    except ValueError as e:
        logger.error(f"Database not initialized: {e}")
        raise HTTPException(
            status_code=503,
            detail="База данн�� не на�т�оена. �ожалуй�та, на�т�ойте DATABASE_URL в пе�еменн�� ок�ужен��."
        )
    except Exception as e:
        logger.error(f"Error getting user {telegram_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ош��ка п�� получен�� данн�� пол�зовател�: {str(e)}"
        )
@app.post("/api/generate/image", response_model=GenerateImageResponse)
async def generate_image(
    request: GenerateImageRequest,
    session: AsyncSession = Depends(get_session)
):
    try:
        logger.info(f"Received image generation request: telegram_id={request.telegram_id}, prompt={request.prompt[:50]}...")
    except Exception as e:
        logger.error(f"Error in generate_image endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
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
            detail=f"Зап�о� отклонен: {reason}\n\n"
                   "�ожалуй�та, ознаком�те�� � пол�т�кой контента (/help в �оте)."
        )
    user = await user_service.get_or_create_user(
        session,
        telegram_id=request.telegram_id
    )
    plan_type = getattr(user, 'plan_type', 'basic')
    if plan_type == 'basic':
        images_used = getattr(user, 'images_used', 0)
        if images_used >= 5:
            raise HTTPException(
                status_code=403,
                detail="�о�т��нут л�м�т �азово�о та��фа: мак��мум 5 �зо��ажен�й. О�нов�те та��ф до �танда�т дл� нео��ан�ченно�о ��пол�зован��."
            )
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
        logger.info(f"Calling image_generation_service.generate_image with provider={image_generation_service.provider}, has_replicate_key={bool(image_generation_service.replicate_key)}")
        result = await image_generation_service.generate_image(
            prompt=request.prompt,
            model=request.model or "flux",
            style=request.style,
            width=request.width,
            height=request.height
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
    user = await user_service.get_or_create_user(
        session,
        telegram_id=telegram_id
    )
    plan_type = getattr(user, 'plan_type', 'basic')
    if plan_type == 'basic':
        videos_used = getattr(user, 'videos_used', 0)
        if videos_used >= 2:
            raise HTTPException(
                status_code=403,
                detail="�о�т��нут л�м�т �азово�о та��фа: мак��мум 2 в�део. О�нов�те та��ф до �танда�т дл� нео��ан�ченно�о ��пол�зован��."
            )
    try:
        uploads_dir = BASE_DIR / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        source_path = uploads_dir / f"{uuid.uuid4()}_{source_image.filename}"
        target_path = uploads_dir / f"{uuid.uuid4()}_{target_video.filename}"
        with open(source_path, "wb") as f:
            f.write(await source_image.read())
        with open(target_path, "wb") as f:
            f.write(await target_video.read())
        generation = Generation(
            user_id=user.id,
            generation_type="deepfake",
            source_file=str(source_path),
            target_file=str(target_path),
            cost=0,
            status="processing"
        )
        session.add(generation)
        await session.commit()
        output_dir = BASE_DIR / "generated"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{uuid.uuid4()}_result.mp4"
        result = await deepface_service.swap_face(
            str(source_path),
            str(target_path),
            str(output_path)
        )
        if result["status"] == "success":
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
    try:
        result = await deepface_service.check_task_status(task_id)
        return result
    except Exception as e:
        logger.error(f"Error checking deepfake task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/models")
async def get_models():
    models = await image_generation_service.get_available_models()
    return {"models": models}
@app.get("/api/styles")
async def get_styles():
    styles = await image_generation_service.get_available_styles()
    return {"styles": styles}
@app.post("/api/generate/video", response_model=GenerateVideoResponse)
async def generate_video(
    request: GenerateVideoRequest,
    session: AsyncSession = Depends(get_session)
):
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
            detail=f"Зап�о� отклонен: {reason}\n\n"
                   "�ожалуй�та, ознаком�те�� � пол�т�кой контента (/help в �оте)."
        )
    user = await user_service.get_or_create_user(
        session,
        telegram_id=request.telegram_id
    )
    plan_type = getattr(user, 'plan_type', 'basic')
    if plan_type == 'basic':
        videos_used = getattr(user, 'videos_used', 0)
        if videos_used >= 2:
            raise HTTPException(
                status_code=403,
                detail="�о�т��нут л�м�т �азово�о та��фа: мак��мум 2 в�део. О�нов�те та��ф до �танда�т дл� нео��ан�ченно�о ��пол�зован��."
            )
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
            user.total_generations += 1
            plan_type = getattr(user, 'plan_type', 'basic')
            if plan_type == 'basic':
                user.videos_used = getattr(user, 'videos_used', 0) + 1
            generation.status = "completed"
            generation.result_file = result.get("video_url") or result.get("video")
            if result.get("task_id"):
                generation.error_message = f"task_id:{result['task_id']}"
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
    try:
        result = await video_generation_service.check_video_task_status(task_id)
        return result
    except Exception as e:
        logger.error(f"Error checking video task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/video/models")
async def get_video_models():
    models = await video_generation_service.get_available_video_models()
    return {"models": models}
@app.get("/api/video/styles")
async def get_video_styles():
    styles = await video_generation_service.get_available_video_styles()
    return {"styles": styles}
@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(
    session: AsyncSession = Depends(get_session)
):
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
    user = await user_service.get_user_by_telegram_id(session, telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.plan_type = "basic"
    user.plan_activated_at = datetime.utcnow()
    user.images_used = 0
    user.videos_used = 0
    await session.commit()
    logger.info(f"Activated basic plan for user {telegram_id}")
    return ActivatePlanResponse(
        success=True,
        message="Базов�й та��ф у�пешно акт�в��ован!",
        plan_type="basic"
    )
@app.get("/api/referral/qr")
async def generate_referral_qr(
    telegram_id: int = Query(..., description="Telegram ID пол�зовател�"),
    session: AsyncSession = Depends(get_session)
):
    try:
        user = await user_service.get_or_create_user(
            session,
            telegram_id=telegram_id
        )
        if not user.referral_code:
            logger.warning(f"User {telegram_id} has no referral_code in QR endpoint, generating one...")
            new_referral_code = user_service.generate_referral_code()
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
            logger.info(f"Generated referral_code {new_referral_code} for user {telegram_id} in QR endpoint")
        referral_code = user.referral_code
        webapp_url = settings.WEBAPP_URL or "https://facy-app.vercel.app"
        referral_link = f"{webapp_url}?ref={referral_code}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(referral_link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
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
@app.post("/api/auth/send-verification-code", response_model=SendVerificationCodeResponse)
async def send_verification_code(
    request: SendVerificationCodeRequest,
    session: AsyncSession = Depends(get_session)
):
    try:
        success, error_message = await user_service.send_verification_code(
            session,
            telegram_id=request.telegram_id,
            email=request.email
        )
        if success:
            return SendVerificationCodeResponse(
                success=True,
                message="�од подтве�жден�� отп�авлен на ваш email"
            )
        else:
            raise HTTPException(status_code=400, detail=error_message or "�е удало�� отп�ав�т� код")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending verification code: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/api/auth/verify-email-code", response_model=VerifyEmailCodeResponse)
async def verify_email_code(
    request: VerifyEmailCodeRequest,
    session: AsyncSession = Depends(get_session)
):
    try:
        success, error_message = await user_service.verify_email_code(
            session,
            telegram_id=request.telegram_id,
            code=request.code
        )
        if success:
            user = await user_service.get_user_by_telegram_id(session, request.telegram_id)
            return VerifyEmailCodeResponse(
                success=True,
                message="Email у�пешно подтве�жден!",
                email_verified=True
            )
        else:
            raise HTTPException(status_code=400, detail=error_message or "�еве�н�й код")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying email code: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/api/remove-background")
async def remove_background(
    image: UploadFile = File(...),
    threshold: int = Query(240, ge=0, le=255, description="�о�о� дл� оп�еделен�� �ело�о цвета")
):
    try:
        image_bytes = await image.read()
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
    health_status = {
        "status": "healthy",
        "database": "unknown"
    }
    try:
        if settings.DATABASE_URL:
            from database import get_engine
            engine = get_engine()
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            health_status["database"] = "connected"
        else:
            health_status["database"] = "not_configured"
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["database"] = "error"
        health_status["database_error"] = str(e)
        health_status["status"] = "degraded"
    return health_status
@app.get("/api/health")
async def api_health_check():
    try:
        db_status = "unknown"
        db_error = None
        if not settings.DATABASE_URL:
            db_status = "not_configured"
            db_error = "DATABASE_URL не у�тановлен"
        else:
            try:
                from database import get_engine
                engine = get_engine()
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                db_status = "connected"
            except ValueError as e:
                db_status = "not_initialized"
                db_error = str(e)
            except Exception as e:
                db_status = "error"
                db_error = str(e)
        return {
            "status": "ok" if db_status == "connected" else "degraded",
            "database": {
                "status": db_status,
                "error": db_error,
                "configured": bool(settings.DATABASE_URL)
            },
            "api": "operational"
        }
    except Exception as e:
        logger.error(f"API health check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
