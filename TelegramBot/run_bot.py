import asyncio
from create_bot import bot, dp

from handlers import insert_user_data
from handlers import main_handler
from handlers import create_request
from handlers import check_packages


async def main():
    dp.include_router(insert_user_data.router)
    dp.include_router(main_handler.router)
    dp.include_router(create_request.router)
    dp.include_router(check_packages.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())