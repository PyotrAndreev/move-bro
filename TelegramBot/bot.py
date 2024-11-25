import asyncio
import logging


from config import config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import insert_user_data
from handlers import main_handler
from handlers import orders_catalogue
async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(insert_user_data.router, main_handler.router, orders_catalogue.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())