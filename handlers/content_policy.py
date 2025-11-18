"""О��а�отч�к� пол�т�к� контента"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services import content_moderation

router = Router()


@router.callback_query(F.data == "content_policy")
async def show_content_policy(callback: CallbackQuery):
    """�оказат� пол�т�ку контента"""
    
    policy_text = content_moderation.get_content_policy()
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="� �о�ла�ен", callback_data="policy_accepted"),
        InlineKeyboardButton(text="�азад", callback_data="help")
    )
    
    await callback.message.edit_text(
        policy_text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "policy_accepted")
async def policy_accepted(callback: CallbackQuery):
    """�одтве�жден�е п��н�т�� пол�т�к�"""
    
    await callback.answer("�па���о за пон�ман�е!", show_alert=True)
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="�лавное мен�", callback_data="back_to_main")
    )
    
    await callback.message.edit_text(
        "<b>�� п��н�л� пол�т�ку контента</b>\n\n"
        "Тепе�� в� можете ��пол�зоват� в�е функц�� п��ложен��.\n"
        "�омн�те: �е�в�� п�едназначен дл� тво�че�тва � ле�ал�но�о ��пол�зован��.",
        reply_markup=builder.as_markup()
    )

