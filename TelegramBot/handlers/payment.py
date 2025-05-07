from aiogram import Bot, Router, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, ReplyKeyboardMarkup, KeyboardButton
from TelegramBot.config import config
from TelegramBot.enum_types import *
from TelegramBot.data_base import Package, get_db
from sqlalchemy.orm import Session

router = Router()

async def send_payment_invoice(bot: Bot, chat_id: int, order_id):
    db: Session = next(get_db())
    order = db.query(Package).filter(
        Package.package_id == order_id
    ).first()
    if (order.purchase_status == PaymentStatusEnum.complete):
        await bot.send_message(chat_id, "Этот заказ уже оплачен.")
        return
    await bot.send_invoice(
        chat_id=chat_id,
        title="Оплата заказа",
        description=f"Заказ #{order_id} - доставка ({order.shipping_country}, {order.shipping_city} - {order.delivery_country}, {order.delivery_city})",
        payload=f"delivery_{order_id}",
        provider_token=config.provider_token.get_secret_value(),
        currency="RUB",
        prices=[LabeledPrice(label="Доставка", amount=(order.cost * 100))],
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
    payload = message.successful_payment.invoice_payload
    try:
        _, order_id_str = payload.split("_")
        order_id = int(order_id_str)
    except Exception as e:
        print("Ошибка при разборе payload:", e)
        return

    db = next(get_db())
    order = db.query(Package).filter(Package.package_id == order_id).first()

    if order:
        order.purchase_status = PaymentStatusEnum.complete
        db.commit()
        print("заказ все")
    else:
        await message.answer("Ошибка: заказ не найден.")