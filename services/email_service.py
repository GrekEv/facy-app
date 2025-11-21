"""РРµСРІРС РґР»С РѕС‚РїСР°РІРєР email"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """РРµСРІРС РґР»С РѕС‚РїСР°РІРєР email"""
    
    @staticmethod
    async def send_verification_code(email: str, code: str) -> bool:
        """
        РћС‚РїСР°РІРС‚С РєРѕРґ РїРѕРґС‚РІРµСР¶РґРµРЅРС РЅР° email
        
        Args:
            email: Email РїРѕР»СѓС‡Р°С‚РµР»С
            code: РРѕРґ РїРѕРґС‚РІРµСР¶РґРµРЅРС
            
        Returns:
            True РµСР»Р РѕС‚РїСР°РІР»РµРЅРѕ СѓСРїРµС€РЅРѕ, False РІ РїСРѕС‚РРІРЅРѕРј СР»СѓС‡Р°Рµ
        """
        try:
            # РСРѕРІРµССРµРј РЅР°СС‚СРѕР№РєР SMTP
            if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
                logger.error("SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD in .env")
                return False
            
            # Р¤РѕСРјРССѓРµРј СРѕРѕРСРµРЅРРµ
            msg = MIMEMultipart()
            msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
            msg['To'] = email
            msg['Subject'] = "РРѕРґ РїРѕРґС‚РІРµСР¶РґРµРЅРС OnlyFace"
            
            # РўРµРєСС‚ РїРССРјР°
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #6366f1;">РРѕРґ РїРѕРґС‚РІРµСР¶РґРµРЅРС OnlyFace</h2>
                    <p>Р—РґСР°РІСС‚РІСѓР№С‚Рµ!</p>
                    <p>РР°С€ РєРѕРґ РїРѕРґС‚РІРµСР¶РґРµРЅРС РґР»С РІСРѕРґР° РІ OnlyFace:</p>
                    <div style="background-color: #f3f4f6; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                        <h1 style="color: #6366f1; font-size: 32px; letter-spacing: 5px; margin: 0;">{code}</h1>
                    </div>
                    <p>РРІРµРґРС‚Рµ СС‚РѕС‚ РєРѕРґ РІ РїСРР»РѕР¶РµРЅРР РґР»С РїРѕРґС‚РІРµСР¶РґРµРЅРС РІР°С€РµРРѕ email.</p>
                    <p>РРѕРґ РґРµР№СС‚РІРС‚РµР»РµРЅ РІ С‚РµС‡РµРЅРРµ 10 РјРРЅСѓС‚.</p>
                    <p style="color: #666; font-size: 12px; margin-top: 30px;">
                        Р•СР»Р РІС РЅРµ Р·Р°РїСР°С€РРІР°Р»Р СС‚РѕС‚ РєРѕРґ, РїСРѕСС‚Рѕ РїСРѕРРРЅРѕСРССѓР№С‚Рµ СС‚Рѕ РїРССРјРѕ.
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # РћС‚РїСР°РІР»СРµРј С‡РµСРµР· SMTP
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
        РСРѕСС‚Р°С РІР°Р»РРґР°С†РС email
        
        Args:
            email: Email РґР»С РїСРѕРІРµСРєР
            
        Returns:
            True РµСР»Р email РІР°Р»РРґРµРЅ
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

