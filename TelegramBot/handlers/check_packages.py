from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from TelegramBot.create_bot import bot
from TelegramBot.data_base import User, Package
from TelegramBot.data_base import get_db
from sqlalchemy.orm import Session

router = Router()

class Form(StatesGroup):
    weight = State()

@router.callback_query(F.data=="track")
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
