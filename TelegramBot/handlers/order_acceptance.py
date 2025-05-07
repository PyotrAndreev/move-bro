from aiogram import Router, F
from TelegramBot.data_base import get_db, Package, Courier
from sqlalchemy.orm import Session
from aiogram.types import CallbackQuery
from TelegramBot.create_bot import bot
from TelegramBot.enum_types import PackageStatusEnum

router = Router()
@router.callback_query(F.data.contains('accept_enroll_'))
async def enroll_accepted(c: CallbackQuery):
    await c.message.delete()
    button_data = c.data.split('_')
    package_id = button_data[2]
    courier_id = button_data[3]
    db: Session = next(get_db())
    package = db.query(Package).filter(Package.package_id == int(package_id)).first()
    courier: Courier = db.query(Courier).filter(Courier.user_id == int(courier_id)).first()
    courier_tg_id = courier.user.telegram_id
    package.courier = courier
    db.commit()
    await bot.send_message(courier_tg_id, f'Обновление по заказу #{package_id}: покупатель одобрил сделку! ')
    await c.message.answer('Уведомили курьера о сделке!')