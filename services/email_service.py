"""�е�в�� дл� отп�авк� email"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """�е�в�� дл� отп�авк� email"""
    
    @staticmethod
    async def send_verification_code(email: str, code: str) -> bool:
        """
        Отп�ав�т� код подтве�жден�� на email
        
        Args:
            email: Email получател�
            code: �од подтве�жден��
            
        Returns:
            True е�л� отп�авлено у�пешно, False в п�от�вном �лучае
        """
        try:
            # ��ове��ем на�т�ойк� SMTP
            if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
                logger.error("SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD in .env")
                return False
            
            # Фо�м��уем �оо��ен�е
            msg = MIMEMultipart()
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
            msg['To'] = email
            msg['Subject'] = "�од подтве�жден�� OnlyFace"
            
            # Тек�т п���ма
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #6366f1;">�од подтве�жден�� OnlyFace</h2>
                    <p>Зд�ав�твуйте!</p>
                    <p>�аш код подтве�жден�� дл� в�ода в OnlyFace:</p>
                    <div style="background-color: #f3f4f6; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                        <h1 style="color: #6366f1; font-size: 32px; letter-spacing: 5px; margin: 0;">{code}</h1>
                    </div>
                    <p>�вед�те �тот код в п��ложен�� дл� подтве�жден�� ваше�о email.</p>
                    <p>�од дей�тв�телен в течен�е 10 м�нут.</p>
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        Е�л� в� не зап�аш�вал� �тот код, п�о�то п�о��но���уйте �то п���мо.
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Отп�авл�ем че�ез SMTP
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
        ��о�та� вал�дац�� email
        
        Args:
            email: Email дл� п�ове�к�
            
        Returns:
            True е�л� email вал�ден
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

