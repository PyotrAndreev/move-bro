import asyncio
from TelegramBot.create_bot import bot, dp

from TelegramBot.handlers import insert_user_data, main_handler, courier_menu, new_create_request, check_packages, new_catalogue, package_choice, order_acceptance, feedback, feedback_menu, sent_feedback, payment, create_journey, check_journeys, find_journey, confirmation
from aiogram_dialog import setup_dialogs

async def main():
    dp.include_router(insert_user_data.router)
    dp.include_router(courier_menu.dialog_router)
    dp.include_router(main_handler.router)
    dp.include_router(new_create_request.router)
    dp.include_router(check_packages.dialog_router)
    dp.include_router(new_catalogue.dialog_router)
    dp.include_router(package_choice.router)
    dp.include_router(order_acceptance.router)
    dp.include_router(feedback.router)
    dp.include_router(feedback_menu.router)
    dp.include_router(sent_feedback.router)
    dp.include_router(payment.router)
    dp.include_router(create_journey.router)
    dp.include_router(check_journeys.dialog_router)
    dp.include_router(find_journey.dialog_router)
    dp.include_router(confirmation.router)
    setup_dialogs(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())