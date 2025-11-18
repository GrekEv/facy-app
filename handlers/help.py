from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
router = Router()
@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
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
