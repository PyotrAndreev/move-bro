# Создаём бота
from aiogram import Bot, Dispatcher
import asyncio
import logging
# config - объект с токеном бота
from TelegramBot.config import config
# MemoryStorage хранит данные форм в оперативной памяти, в проде лучше использовать RedisStorage(соответственно нужен Redis)
from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.fsm.storage.redis import RedisStorage
# Импортируем части кода, отвечающие за определённые хэндлеры
import basic_handler
async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.token.get_secret_value())
    # Говорим диспетчеру, что мы храним данные форм в оперативной памяти(в MemoryStorage())
    dp = Dispatcher(storage=MemoryStorage())
    # Добавляем роутеры(мини-диспетчеры) в dispatcher
    dp.include_routers(basic_handler.router, dialog_handler.router)
    # Запускаем бота
    await dp.start_polling(bot)
# Запускаем бота
if __name__ == "__main__":
    asyncio.run(main())
