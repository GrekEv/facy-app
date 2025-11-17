"""Обработчики команды /start"""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import settings
import logging

logger = logging.getLogger(__name__)

router = Router()


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Получить главную клавиатуру"""
    builder = InlineKeyboardBuilder()
    
    # Получаем URL Web App (с автоматическим определением)
    webapp_url = settings.webapp_url
    
    # Кнопка для открытия Web App
    builder.row(
        InlineKeyboardButton(
            text="Открыть приложение",
            web_app=WebAppInfo(url=webapp_url)
        )
    )
    
    builder.row(
        InlineKeyboardButton(text="Мой баланс", callback_data="balance"),
        InlineKeyboardButton(text="Статистика", callback_data="stats")
    )
    
    builder.row(
        InlineKeyboardButton(text="Купить поинты", callback_data="buy_points"),
    )
    
    builder.row(
        InlineKeyboardButton(text="Помощь", callback_data="help")
    )
    
    return builder.as_markup()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработка команды /start"""
    user = message.from_user
    
    welcome_text = f"""
<b>Привет, {user.first_name}!</b>

Добро пожаловать в <b>DeepFace</b> — инструмент для:

<b>Замены лиц в видео</b> (DeepFake)
• Заменяй лица в любых видео
• Профессиональное качество
• Быстрая обработка

<b>Генерации изображений</b>
• Создавай уникальные изображения по описанию
• Множество стилей и моделей
• Высокое разрешение

<b>Бонус для новых пользователей:</b>
• 50 поинтов на старте
• 1 бесплатная генерация

Нажми на кнопку ниже, чтобы начать!
"""
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback):
    """Вернуться в главное меню"""
    await callback.message.edit_text(
        "<b>Главное меню</b>\n\nВыберите действие:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

