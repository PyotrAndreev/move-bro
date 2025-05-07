#sent_feedback.py
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session
import asyncio
from TelegramBot.enum_types import *
from TelegramBot.data_base import Logging, User, get_db
from TelegramBot.keyboards import keyboards
from datetime import datetime

router = Router()


class SentFeedbackStates(StatesGroup):
    waiting_feedback = State()

async def delete_previous_messages(chat_id: int, message_ids: list, bot: Bot):
    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception as e:
            print(f"Error deleting message {msg_id}: {str(e)}")

@router.callback_query(F.data == "sent_feedback")
async def feedback_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    db: Session = next(get_db())
    user_tg_id = callback.from_user.id
    feedback_logs = db.query(Logging).filter(
        Logging.log_type == LogTypeEnum.FEEDBACK,
        Logging.user_id == user_tg_id
    ).all()

    await callback.message.delete()
    if not feedback_logs:
        tickets = "У вас нет активных тикетов"
    else:
        tickets = '\n'.join(f"{i + 1}. {feedback_logs[i].log_text}" for i in range(len(feedback_logs)))
    msg = await callback.message.answer(
        tickets,
        reply_markup=keyboards.sent_feedback()
    )
    await state.set_state(SentFeedbackStates.waiting_feedback)
    await state.update_data(messages_to_delete=[msg.message_id])
    await callback.answer()

@router.callback_query(F.data == "cancel_sent_feedback", SentFeedbackStates.waiting_feedback)
async def cancel_feedback_menu(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])

    await delete_previous_messages(callback.message.chat.id, messages_to_delete, bot)
    await state.clear()

    # Возвращаем главное меню
    await callback.message.answer(
        "Меню заказчика:",
        reply_markup=keyboards.user_menu()
    )
    await callback.answer()