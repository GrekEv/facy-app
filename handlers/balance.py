"""Обработчики для работы с балансом"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_session
from services import user_service
import logging

logger = logging.getLogger(__name__)

router = Router()


def get_balance_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для баланса"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💎 Купить поинты", callback_data="buy_points")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    )
    
    return builder.as_markup()


def get_buy_points_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для покупки поинтов"""
    builder = InlineKeyboardBuilder()
    
    # Пакеты поинтов
    builder.row(
        InlineKeyboardButton(text="100 поинтов - 99₽", callback_data="buy_100")
    )
    builder.row(
        InlineKeyboardButton(text="500 поинтов - 399₽", callback_data="buy_500")
    )
    builder.row(
        InlineKeyboardButton(text="1000 поинтов - 699₽", callback_data="buy_1000")
    )
    builder.row(
        InlineKeyboardButton(text="2500 поинтов - 1499₽", callback_data="buy_2500")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="balance")
    )
    
    return builder.as_markup()


@router.callback_query(F.data == "balance")
async def show_balance(callback: CallbackQuery):
    """Показать баланс пользователя"""
    async for session in get_session():
        user = await user_service.get_user_by_telegram_id(
            session,
            callback.from_user.id
        )
        
        if not user:
            await callback.answer("❌ Ошибка: пользователь не найден", show_alert=True)
            return
        
        balance_text = f"""
💰 <b>Ваш баланс</b>

💎 Поинты: <b>{user.balance}</b>
🎁 Бесплатных генераций: <b>{user.free_generations}</b>

📊 <b>Статистика использования:</b>
• Всего генераций изображений: {user.total_generations}
• Всего DeepFake видео: {user.total_deepfakes}

💡 <b>Стоимость услуг:</b>
• Генерация изображения: 10 поинтов
• DeepFake видео: 50 поинтов
"""
        
        if user.is_premium:
            balance_text += f"\n⭐ <b>Premium статус активен</b>"
        
        await callback.message.edit_text(
            balance_text,
            reply_markup=get_balance_keyboard()
        )
    
    await callback.answer()


@router.callback_query(F.data == "buy_points")
async def show_buy_points(callback: CallbackQuery):
    """Показать варианты покупки поинтов"""
    text = """
💎 <b>Покупка поинтов</b>

Выберите подходящий пакет:

💡 <b>Что можно сделать с поинтами:</b>
• 10 поинтов = 1 генерация изображения
• 50 поинтов = 1 DeepFake видео

🎁 Чем больше пакет — тем выгоднее!
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_buy_points_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_"))
async def process_buy_points(callback: CallbackQuery):
    """Обработка покупки поинтов"""
    # Извлекаем количество поинтов
    amount_str = callback.data.replace("buy_", "")
    
    packages = {
        "100": {"points": 100, "price": 99},
        "500": {"points": 500, "price": 399},
        "1000": {"points": 1000, "price": 699},
        "2500": {"points": 2500, "price": 1499}
    }
    
    if amount_str not in packages:
        await callback.answer("❌ Неверный пакет", show_alert=True)
        return
    
    package = packages[amount_str]
    
    # Здесь должна быть интеграция с платежной системой
    # Пока что показываем информационное сообщение
    
    text = f"""
💎 <b>Покупка {package['points']} поинтов</b>

💰 Стоимость: <b>{package['price']}₽</b>

⚠️ <b>Функция оплаты в разработке</b>

Для активации платежей необходимо:
1. Подключить Telegram Payments
2. Настроить платежного провайдера
3. Получить токен платежной системы

Свяжитесь с администратором для подключения платежей.
"""
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="buy_points")
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    """Показать статистику пользователя"""
    async for session in get_session():
        user = await user_service.get_user_by_telegram_id(
            session,
            callback.from_user.id
        )
        
        if not user:
            await callback.answer("❌ Ошибка: пользователь не найден", show_alert=True)
            return
        
        stats_text = f"""
📊 <b>Ваша статистика</b>

👤 <b>Профиль:</b>
• ID: {user.telegram_id}
• Имя: {user.first_name or 'Не указано'}
• Username: @{user.username or 'Не указано'}

💎 <b>Баланс:</b>
• Поинты: {user.balance}
• Бесплатных генераций: {user.free_generations}

🎨 <b>Активность:</b>
• Генераций изображений: {user.total_generations}
• DeepFake видео: {user.total_deepfakes}
• Всего операций: {user.total_generations + user.total_deepfakes}

📅 <b>Даты:</b>
• Регистрация: {user.created_at.strftime('%d.%m.%Y')}
• Последняя активность: {user.last_active.strftime('%d.%m.%Y %H:%M')}
"""
        
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
        )
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=builder.as_markup()
        )
    
    await callback.answer()

