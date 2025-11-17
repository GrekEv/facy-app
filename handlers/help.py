"""Обработчики помощи"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """Показать помощь"""
    
    help_text = """
<b>Помощь</b>

<b>DeepFake - Замена лица в видео:</b>

1. Откройте приложение
2. Выберите раздел "DeepFake Video"
3. Загрузите фото с лицом
4. Загрузите видео, в котором хотите заменить лицо
5. Нажмите "Создать" и дождитесь результата

Стоимость: <b>50 поинтов</b>

<b>Генерация изображений:</b>

1. Откройте приложение
2. Выберите раздел "Генерация изображений"
3. Опишите желаемое изображение
4. Выберите модель и стиль
5. Нажмите "Сгенерировать"

Стоимость: <b>10 поинтов</b>

<b>Получение поинтов:</b>

• 50 поинтов при регистрации
• 1 бесплатная генерация
• Покупка пакетов поинтов

<b>Советы:</b>

• Используйте качественные фото для лучшего результата
• Чем подробнее описание, тем лучше генерация
• Экспериментируйте со стилями и моделями
• Публикуйте результаты в галерее и получайте лайки

<b>Нужна помощь?</b>

Свяжитесь с поддержкой: @your_support
"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Политика контента", callback_data="content_policy")
    )
    builder.row(
        InlineKeyboardButton(text="Назад", callback_data="back_to_main")
    )
    
    await callback.message.edit_text(
        help_text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()

