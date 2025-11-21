"""РРѕРґСѓР»С РѕРСР°РРѕС‚С‡РРєРѕРІ"""
from aiogram import Router
from . import start, balance, help, content_policy, payments

# РРѕР·РґР°РµРј РР»Р°РІРЅСР№ СРѕСѓС‚РµС
main_router = Router()

# РРѕРґРєР»СС‡Р°РµРј РІСРµ СРѕСѓС‚РµСС
main_router.include_router(start.router)
main_router.include_router(balance.router)
main_router.include_router(help.router)
main_router.include_router(content_policy.router)
main_router.include_router(payments.router)

