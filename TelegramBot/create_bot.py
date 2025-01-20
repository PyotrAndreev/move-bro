import logging
from TelegramBot.config import config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

bot = Bot(token=config.token.get_secret_value())
dp = Dispatcher(storage=RedisStorage(config.redis_storage.get_secret_value()))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)