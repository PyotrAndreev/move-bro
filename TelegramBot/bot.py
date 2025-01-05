import asyncio
import logging
from TelegramBot.config import config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import insert_user_data
from handlers import main_handler
from handlers import package_choice
from handlers import orderscatalogue
from handlers import create_request
from handlers import check_packages

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(insert_user_data.router)
    dp.include_router(main_handler.router)
    dp.include_router(package_choice.router)
    dp.include_routers(orderscatalogue.router)
    dp.include_router(create_request.router)
    dp.include_router(check_packages.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())