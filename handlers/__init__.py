"""Модуль обработчиков"""
from aiogram import Router
from . import start, balance, help, content_policy, payments

# Создаем главный роутер
main_router = Router()

# Подключаем все роутеры
main_router.include_router(start.router)
main_router.include_router(balance.router)
main_router.include_router(help.router)
main_router.include_router(content_policy.router)
main_router.include_router(payments.router)

