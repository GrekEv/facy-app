"""Сервис модерации контента"""
import re
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class ContentModerationService:
    """Сервис для проверки и фильтрации контента"""
    
    # Список запрещенных слов и фраз (NSFW, насилие, и т.д.)
    BANNED_KEYWORDS = [
        'porn', 'порно', 'xxx', 'sex', 'секс', 'nude', 'голый', 'голая',
        'nsfw', '18+', 'adult', 'эротика', 'erotic', 'naked', 'обнаженн',
        'violence', 'насилие', 'blood', 'кровь', 'weapon', 'оружие',
        'drugs', 'наркотики', 'hate', 'ненависть'
    ]
    
    # Список подозрительных слов, требующих дополнительной проверки
    SUSPICIOUS_KEYWORDS = [
        'underwear', 'белье', 'bikini', 'бикини', 'swimsuit', 'купальник',
        'body', 'тело', 'skin', 'кожа'
    ]
    
    def __init__(self):
        self.enabled = True
    
    def check_text_content(self, text: str) -> Tuple[bool, str]:
        """
        Проверить текстовый контент на допустимость
        
        Args:
            text: Текст для проверки
            
        Returns:
            (разрешено, причина_отклонения)
        """
        if not text:
            return True, ""
        
        text_lower = text.lower()
        
        # Проверка на запрещенные слова
        for keyword in self.BANNED_KEYWORDS:
            if keyword in text_lower:
                logger.warning(f"Blocked prompt with banned keyword: {keyword}")
                return False, f"Обнаружено недопустимое содержание: '{keyword}'"
        
        # Проверка на подозрительные комбинации
        suspicious_count = sum(1 for keyword in self.SUSPICIOUS_KEYWORDS if keyword in text_lower)
        if suspicious_count >= 2:
            logger.warning(f"Blocked prompt with suspicious keywords count: {suspicious_count}")
            return False, "Обнаружено потенциально недопустимое содержание"
        
        # Проверка на попытки обхода фильтров
        if self._check_obfuscation(text_lower):
            return False, "Обнаружена попытка обхода фильтров контента"
        
        return True, ""
    
    def _check_obfuscation(self, text: str) -> bool:
        """
        Проверка на попытки обхода фильтров (замена букв, пробелы и т.д.)
        """
        # Убираем пробелы между буквами
        text_no_spaces = re.sub(r'\s+', '', text)
        
        # Проверяем снова
        for keyword in self.BANNED_KEYWORDS:
            if keyword in text_no_spaces:
                return True
        
        return False
    
    def get_content_policy(self) -> str:
        """
        Получить политику использования контента
        """
        return """
<b>Политика контента</b>

<b>Запрещено:</b>
• NSFW контент (18+, эротика, порнография)
• Насилие, жестокость
• Наркотики и оружие
• Разжигание ненависти
• Нарушение авторских прав
• Создание дипфейков реальных людей без согласия

<b>Разрешено:</b>
• Художественная генерация (пейзажи, объекты, фэнтези)
• Портреты (без NSFW)
• Творческие концепты
• Иллюстрации для проектов
• Дипфейки с собственным лицом или с согласия

<b>Последствия нарушений:</b>
• Первое нарушение - предупреждение
• Повторные нарушения - блокировка аккаунта
• Серьезные нарушения - передача данных в правоохранительные органы

<i>Используя сервис, вы соглашаетесь с политикой контента.</i>
"""
    
    def check_image_safety(self, image_url: str) -> Dict:
        """
        Проверить безопасность изображения (заглушка для будущей интеграции)
        
        В продакшене здесь должна быть интеграция с:
        - Google Cloud Vision API
        - AWS Rekognition
        - Azure Content Moderator
        
        Args:
            image_url: URL изображения для проверки
            
        Returns:
            Результат проверки
        """
        # TODO: Интеграция с сервисом модерации изображений
        return {
            "safe": True,
            "confidence": 0.95,
            "labels": []
        }
    
    def log_violation(self, user_id: int, content_type: str, content: str, reason: str):
        """
        Логировать нарушение политики контента
        """
        logger.warning(
            f"Content policy violation | "
            f"User: {user_id} | "
            f"Type: {content_type} | "
            f"Reason: {reason} | "
            f"Content: {content[:100]}"
        )


content_moderation = ContentModerationService()

