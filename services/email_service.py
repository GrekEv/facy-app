"""Сервис для отправки email"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email"""
    
    @staticmethod
    async def send_verification_code(email: str, code: str) -> bool:
        """
        Отправить код подтверждения на email
        
        Args:
            email: Email получателя
            code: Код подтверждения
            
        Returns:
            True если отправлено успешно, False в противном случае
        """
        try:
            # Проверяем настройки SMTP
            if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
                logger.error("SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD in .env")
                return False
            
            # Формируем сообщение
            msg = MIMEMultipart()
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
            msg['To'] = email
            msg['Subject'] = "Код подтверждения OnlyFace"
            
            # Текст письма
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #6366f1;">Код подтверждения OnlyFace</h2>
                    <p>Здравствуйте!</p>
                    <p>Ваш код подтверждения для входа в OnlyFace:</p>
                    <div style="background-color: #f3f4f6; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                        <h1 style="color: #6366f1; font-size: 32px; letter-spacing: 5px; margin: 0;">{code}</h1>
                    </div>
                    <p>Введите этот код в приложении для подтверждения вашего email.</p>
                    <p>Код действителен в течение 10 минут.</p>
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        Если вы не запрашивали этот код, просто проигнорируйте это письмо.
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Отправляем через SMTP
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Verification code sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending verification code to {email}: {e}")
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Простая валидация email
        
        Args:
            email: Email для проверки
            
        Returns:
            True если email валиден
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

