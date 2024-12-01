import asyncio
import logging
from datetime import date
from TelegramBot.config import config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Bold, Text
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode

from TelegramBot.data_base import get_db
from TelegramBot.data_base import User
from sqlalchemy.orm import Session
from TelegramBot.keyboards import keyboards
from TelegramBot.handlers.main_handler import MainForms

router = Router()

class Form(StatesGroup):
    gender = State()

@router.message(F.text == "Отслеживать посылки", MainForms.choosing)
async def start_request_process(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data.get("cur_user").user_id)