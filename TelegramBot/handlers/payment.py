from aiogram import Bot, Router, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, ReplyKeyboardMarkup, KeyboardButton
from TelegramBot.config import config

router = Router()

@router.callback_query(F.data == "payment")
async def show_payment_menu(callback: types.CallbackQuery, bot: Bot):
    # await callback.message.delete()
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Оплата заказа",
        description="Заказ #069 - доставка (Москва - Новосибирск)",
        payload="delivery",
        provider_token=config.provider_token.get_secret_value(),
        currency="RUB",
        prices=[LabeledPrice(label="Доставка", amount=29900)],
        start_parameter="delivery_payment"
    )


@router.pre_checkout_query()
async def process_pre_checkout(query: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(
        pre_checkout_query_id=query.id,
        ok=True
    )

@router.message(F.content_type == "successful_payment")
async def process_successful_payment(message: types.Message):
    if message.successful_payment.invoice_payload == "premium_monthly":
        await message.answer("✅ Оплата прошла успешно! Доступ активирован.")