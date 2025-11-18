"""�одул� о��а�отч�ков"""
from aiogram import Router
from . import start, balance, help, content_policy, payments

# �оздаем �лавн�й �оуте�
main_router = Router()

# �одкл�чаем в�е �оуте��
main_router.include_router(start.router)
main_router.include_router(balance.router)
main_router.include_router(help.router)
main_router.include_router(content_policy.router)
main_router.include_router(payments.router)

