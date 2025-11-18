"""О��а�отч�к� дл� �а�от� � �алан�ом"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import get_session
from services import user_service
import logging

logger = logging.getLogger(__name__)

router = Router()


def get_balance_keyboard() -> InlineKeyboardMarkup:
    """�лав�ату�а дл� �алан�а"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="�уп�т� по�нт�", callback_data="buy_points")
    )
    builder.row(
        InlineKeyboardButton(text="�азад", callback_data="back_to_main")
    )
    
    return builder.as_markup()


def get_buy_points_keyboard() -> InlineKeyboardMarkup:
    """�лав�ату�а дл� покупк� по�нтов"""
    builder = InlineKeyboardBuilder()
    
    # �акет� по�нтов
    builder.row(
        InlineKeyboardButton(text="100 по�нтов - 99��", callback_data="buy_100")
    )
    builder.row(
        InlineKeyboardButton(text="500 по�нтов - 399��", callback_data="buy_500")
    )
    builder.row(
        InlineKeyboardButton(text="1000 по�нтов - 699��", callback_data="buy_1000")
    )
    builder.row(
        InlineKeyboardButton(text="2500 по�нтов - 1499��", callback_data="buy_2500")
    )
    builder.row(
        InlineKeyboardButton(text="�азад", callback_data="balance")
    )
    
    return builder.as_markup()


@router.callback_query(F.data == "balance")
async def show_balance(callback: CallbackQuery):
    """�оказат� �алан� пол�зовател�"""
    async for session in get_session():
        user = await user_service.get_user_by_telegram_id(
            session,
            callback.from_user.id
        )
        
        if not user:
            await callback.answer("Ош��ка: пол�зовател� не найден", show_alert=True)
            return
        
        balance_text = f"""
<b>�аш �алан�</b>

�о�нт�: <b>{user.balance}</b>
Бе�платн�� �ене�ац�й: <b>{user.free_generations}</b>

<b>�тат��т�ка ��пол�зован��:</b>
� ��е�о �ене�ац�й �зо��ажен�й: {user.total_generations}
� ��е�о DeepFake в�део: {user.total_deepfakes}

<b>�то�мо�т� у�лу�:</b>
� �ене�ац�� �зо��ажен��: 10 по�нтов
� DeepFake в�део: 50 по�нтов
"""
        
        if user.is_premium:
            balance_text += f"\n<b>Premium �тату� акт�вен</b>"
        
        await callback.message.edit_text(
            balance_text,
            reply_markup=get_balance_keyboard()
        )
    
    await callback.answer()


@router.callback_query(F.data == "buy_points")
async def show_buy_points(callback: CallbackQuery):
    """�оказат� ва��ант� покупк� по�нтов"""
    text = """
<b>�окупка по�нтов</b>

���е��те под�од���й пакет:

<b>�то можно �делат� � по�нтам�:</b>
� 10 по�нтов = 1 �ене�ац�� �зо��ажен��
� 50 по�нтов = 1 DeepFake в�део

�ем �ол�ше пакет  тем в��однее!
"""
    
    await callback.message.edit_text(
        text,
        reply_markup=get_buy_points_keyboard()
    )
    await callback.answer()


# О��а�отка покупк� по�нтов пе�ене�ена в handlers/payments.py


@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    """�оказат� �тат��т�ку пол�зовател�"""
    async for session in get_session():
        user = await user_service.get_user_by_telegram_id(
            session,
            callback.from_user.id
        )
        
        if not user:
            await callback.answer("Ош��ка: пол�зовател� не найден", show_alert=True)
            return
        
        stats_text = f"""
<b>�аша �тат��т�ка</b>

<b>��оф�л�:</b>
� ID: {user.telegram_id}
� Им�: {user.first_name or '�е указано'}
� Username: @{user.username or '�е указано'}

<b>Балан�:</b>
� �о�нт�: {user.balance}
� Бе�платн�� �ене�ац�й: {user.free_generations}

<b>�кт�вно�т�:</b>
� �ене�ац�й �зо��ажен�й: {user.total_generations}
� DeepFake в�део: {user.total_deepfakes}
� ��е�о опе�ац�й: {user.total_generations + user.total_deepfakes}

<b>�ат�:</b>
� �е���т�ац��: {user.created_at.strftime('%d.%m.%Y')}
� �о�ледн�� акт�вно�т�: {user.last_active.strftime('%d.%m.%Y %H:%M')}
"""
        
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="�азад", callback_data="back_to_main")
        )
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=builder.as_markup()
        )
    
    await callback.answer()

