import asyncio
import logging
from TelegramBot.config import config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.formatting import Bold, Text
from aiogram.fsm.state import StatesGroup, State
import re

from TelegramBot.data_base import get_db
from TelegramBot.data_base import User
from sqlalchemy.orm import Session
from TelegramBot.keyboards import keyboards

router = Router()


class Form(StatesGroup):
    gender = State()
    first_name = State()
    second_name = State()
    email = State()
    phone = State()
    check = State()
    check_process = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if (user):
        print("hahahha")
        await message.answer("bla bla bla", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="package_choice", callback_data="package_choice")]]))
    else:
        content = Text(
            "👋 Привет! Я твой персональный помощник по сервису MoveBro!. 🚚 \n"
            "С помощью меня ты можешь: \n"
            "1. 📦 Дешево передать посылку через путешественников. \n"
            "2. 🕒 Узнать время доставки и отслеживать свой заказ. \n"
            "3. 💳 Оплатить доставку удобным для тебя способом. \n"
            "4. 🗺️ Стать путешественником и самому помогать другим людям! \n"
            "Чтобы начать, нужно сначала зарегистрироваться."
        )
        await message.answer(
            **content.as_kwargs()
        )
        content = Text("Для начала регистрации нажмите \"Начать\"")
        await message.answer(
            **content.as_kwargs(),
            reply_markup=keyboards.get_ready()
        )
