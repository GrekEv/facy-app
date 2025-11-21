"""РР»Р°РІРЅСР№ РјРѕРґСѓР»С РРѕС‚Р°"""
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import settings
import logging

# РР°СС‚СРѕР№РєР° Р»РѕРРСРѕРІР°РЅРС
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# РРѕР·РґР°РµРј РРѕС‚Р°
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# РРѕР·РґР°РµРј РґРСРїРµС‚С‡РµС
dp = Dispatcher()

