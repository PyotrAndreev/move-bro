from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import Text
from aiogram.fsm.state import StatesGroup, State

from data_base import get_db
from data_base import User
from sqlalchemy.orm import Session
from keyboards import keyboards

router = Router()

class MainForms(StatesGroup):
    choosing = State()
    blank = State()

@router.message(Command("start"))
async def main_cmd_start(message: Message, state: FSMContext):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if (user):
        await state.update_data(cur_user=user)
        content = Text(
            "В данный момент вы находитесь в меню заказчика."
        )
        await message.answer(
            **content.as_kwargs(),
            reply_markup=keyboards.user_menu()
        )
        await state.set_state(MainForms.choosing)
    else:
        content = Text(
            "👋 Привет! Я твой персональный помощник по сервису MoveBro! 🚚 \n"
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
        await state.set_state(MainForms.blank)