import datetime

import aiogram_dialog.api.entities.modes
from aiogram import Router, F, Dispatcher
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import DialogManager, Window, setup_dialogs, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Column, SwitchTo, Back
from aiogram_dialog.widgets.text import Const, Format
from typing import Any
from pyrogram.types import InlineKeyboardButton
from scipy.datasets import download_all

from TelegramBot.data_base import get_db, Package, User, PackageNote, Courier
from sqlalchemy.orm import Session
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog
from TelegramBot.handlers.main_handler import MainForms  # Убедитесь, что MainForms импортируется правильно
from TelegramBot.keyboards import keyboards
from TelegramBot.logging_helper import set_info_log
from TelegramBot.create_bot import bot
from TelegramBot.enum_types import *

router = Router()
@router.callback_query(F.data.contains('accept_enroll_'))
async def enroll_accepted(c: CallbackQuery):
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