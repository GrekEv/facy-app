# -*- coding: utf-8 -*-
"""�е�в�� моде�ац�� контента"""
import re
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class ContentModerationService:
    """�е�в�� дл� п�ове�к� � ф�л�т�ац�� контента"""
    
    # �п��ок зап�е�енн�� �лов � ф�аз (NSFW, на��л�е, � т.д.)
    BANNED_KEYWORDS = [
        'porn', 'по�но', 'xxx', 'sex', '�ек�', 'nude', '�ол�й', '�ола�',
        'nsfw', '18+', 'adult', '��от�ка', 'erotic', 'naked', 'о�наженн',
        'violence', 'на��л�е', 'blood', 'к�ов�', 'weapon', 'о�уж�е',
        'drugs', 'на�кот�к�', 'hate', 'ненав��т�'
    ]
    
    # �п��ок подоз��тел�н�� �лов, т�е�у���� дополн�тел�ной п�ове�к�
    SUSPICIOUS_KEYWORDS = [
        'underwear', '�ел�е', 'bikini', '��к�н�', 'swimsuit', 'купал�н�к',
        'body', 'тело', 'skin', 'кожа'
    ]
    
    def __init__(self):
        self.enabled = True
    
    def check_text_content(self, text: str) -> Tuple[bool, str]:
        """
        ��ове��т� тек�тов�й контент на допу�т�мо�т�
        
        Args:
            text: Тек�т дл� п�ове�к�
            
        Returns:
            (�аз�ешено, п��ч�на_отклонен��)
        """
        if not text:
            return True, ""
        
        text_lower = text.lower()
        
        # ��ове�ка на зап�е�енн�е �лова
        for keyword in self.BANNED_KEYWORDS:
            if keyword in text_lower:
                logger.warning(f"Blocked prompt with banned keyword: {keyword}")
                return False, f"О�на�ужено недопу�т�мое �оде�жан�е: '{keyword}'"
        
        # ��ове�ка на подоз��тел�н�е ком��нац��
        suspicious_count = sum(1 for keyword in self.SUSPICIOUS_KEYWORDS if keyword in text_lower)
        if suspicious_count >= 2:
            logger.warning(f"Blocked prompt with suspicious keywords count: {suspicious_count}")
            return False, "О�на�ужено потенц�ал�но недопу�т�мое �оде�жан�е"
        
        # ��ове�ка на поп�тк� о��ода ф�л�т�ов
        if self._check_obfuscation(text_lower):
            return False, "О�на�ужена поп�тка о��ода ф�л�т�ов контента"
        
        return True, ""
    
    def _check_obfuscation(self, text: str) -> bool:
        """
        ��ове�ка на поп�тк� о��ода ф�л�т�ов (замена �укв, п�о�ел� � т.д.)
        """
        # У���аем п�о�ел� между �уквам�
        text_no_spaces = re.sub(r'\s+', '', text)
        
        # ��ове��ем �нова
        for keyword in self.BANNED_KEYWORDS:
            if keyword in text_no_spaces:
                return True
        
        return False
    
    def get_content_policy(self) -> str:
        """
        �олуч�т� пол�т�ку ��пол�зован�� контента
        """
        return """
<b>�ол�т�ка контента</b>

<b>Зап�е�ено:</b>
� NSFW контент (18+, ��от�ка, по�но��аф��)
� �а��л�е, же�токо�т�
� �а�кот�к� � о�уж�е
� �азж��ан�е ненав��т�
� �а�ушен�е авто��к�� п�ав
� �оздан�е д�пфейков �еал�н�� л�дей �ез �о�ла���

<b>�аз�ешено:</b>
� �удоже�твенна� �ене�ац�� (пейзаж�, о��ект�, ф�нтез�)
� �о�т�ет� (�ез NSFW)
� Тво�че�к�е концепт�
� Илл��т�ац�� дл� п�оектов
� ��пфейк� � �о��твенн�м л�цом �л� � �о�ла���

<b>�о�лед�тв�� на�ушен�й:</b>
� �е�вое на�ушен�е - п�едуп�ежден�е
� �овто�н�е на�ушен�� - �лок��овка аккаунта
� �е��езн�е на�ушен�� - пе�едача данн�� в п�авоо��ан�тел�н�е о��ан�

<i>И�пол�зу� �е�в��, в� �о�лашаете�� � пол�т�кой контента.</i>
"""
    
    def check_image_safety(self, image_url: str) -> Dict:
        """
        ��ове��т� �езопа�но�т� �зо��ажен�� (за�лушка дл� �уду�ей �нте��ац��)
        
        � п�одакшене зде�� должна ��т� �нте��ац�� �:
        - Google Cloud Vision API
        - AWS Rekognition
        - Azure Content Moderator
        
        Args:
            image_url: URL �зо��ажен�� дл� п�ове�к�
            
        Returns:
            �езул�тат п�ове�к�
        """
        # TODO: Инте��ац�� � �е�в��ом моде�ац�� �зо��ажен�й
        return {
            "safe": True,
            "confidence": 0.95,
            "labels": []
        }
    
    def log_violation(self, user_id: int, content_type: str, content: str, reason: str):
        """
        Ло���оват� на�ушен�е пол�т�к� контента
        """
        logger.warning(
            f"Content policy violation | "
            f"User: {user_id} | "
            f"Type: {content_type} | "
            f"Reason: {reason} | "
            f"Content: {content[:100]}"
        )


content_moderation = ContentModerationService()

