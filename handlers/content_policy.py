"""Обработчики политики контента"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services import content_moderation

router = Router()


@router.callback_query(F.data == "content_policy")
async def show_content_policy(callback: CallbackQuery):
    """Показать политику контента"""
    
    policy_text = content_moderation.get_content_policy()
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Я согласен", callback_data="policy_accepted"),
        InlineKeyboardButton(text="Назад", callback_data="help")
    )
    
    await callback.message.edit_text(
        policy_text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "policy_accepted")
async def policy_accepted(callback: CallbackQuery):
    """Подтверждение принятия политики"""
    
    await callback.answer("Спасибо за понимание!", show_alert=True)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Главное меню", callback_data="back_to_main")
    )
    
    await callback.message.edit_text(
        "<b>Вы приняли политику контента</b>\n\n"
        "Теперь вы можете использовать все функции приложения.\n"
        "Помните: сервис предназначен для творчества и легального использования.",
        reply_markup=builder.as_markup()
    )

