import asyncio
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode
from create_bot import bot
import re

from data_base import get_db
from data_base import Package
from sqlalchemy.orm import Session
from keyboards import keyboards
from handlers.main_handler import MainForms

router = Router()

class Form(StatesGroup):
    weight = State()

@router.callback_query(F.data=="track", MainForms.choosing)
async def start_request_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("menu_bot_message"))
    db: Session = next(get_db())
    db_packages = db.query(Package).filter(Package.customer_id == data.get("user_id")).all()
    packages = {}
    for i in range(len(db_packages)):
        pass
    page = 1
    first = True
    if len(packages) <= 5:
        last = True
    else:
        last = False
    