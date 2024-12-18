from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import Text
from aiogram.fsm.state import StatesGroup, State
from create_bot import bot
from aiogram.types import Message, CallbackQuery

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
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if (user):
        await state.update_data(user_id=user.user_id)
        content = Text(
            "Меню заказчика:"
        )
        bot_message = await message.answer(
            **content.as_kwargs(),
            reply_markup=keyboards.user_menu()
        )
        await state.update_data(menu_bot_message=bot_message.message_id)
        await state.set_state(MainForms.choosing)
    else:
        content = Text("👋 Привет! Я твой персональный помощник по сервису MoveBro! 🚚\n Для начала регистрации нажмите \"Начать\"")
        bot_message = await message.answer(
            **content.as_kwargs(),
            reply_markup=keyboards.get_ready()
        )
        await state.update_data(start_registration_bot_message=bot_message.message_id)
        await state.set_state(MainForms.blank)
    db.expunge_all()

@router.message(F.text, MainForms.choosing)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)





@router.callback_query(F.data=="test", MainForms.choosing)
async def start_request_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(data.get("user_id"))
    print(type(data.get("user_id")))