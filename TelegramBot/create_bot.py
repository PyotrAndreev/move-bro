import logging

from aiogram.fsm.storage.base import DefaultKeyBuilder

from TelegramBot.config import config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

bot = Bot(token=config.token.get_secret_value())
#storage=RedisStorage.from_url(config.redis_storage.get_secret_value(), key_builder=DefaultKeyBuilder(with_destiny=True))
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)