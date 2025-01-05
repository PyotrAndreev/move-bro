import asyncio
from TelegramBot.create_bot import bot, dp

from TelegramBot.handlers import insert_user_data, main_handler, new_create_request, check_packages, new_catalogue, package_choice
from aiogram_dialog import setup_dialogs

async def main():
    dp.include_router(insert_user_data.router)
    dp.include_router(main_handler.router)
    dp.include_router(new_create_request.router)
    dp.include_router(check_packages.router)
    dp.include_router(new_catalogue.dialog_router)
    dp.include_router(package_choice.router)
    setup_dialogs(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())