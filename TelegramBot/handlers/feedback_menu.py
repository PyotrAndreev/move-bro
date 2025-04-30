#feedback_menu.py
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session
import asyncio

from TelegramBot.data_base import Logging, User, get_db
from TelegramBot.keyboards import keyboards
from datetime import datetime

router = Router()


class FeedbackMenuStates(StatesGroup):
    waiting_feedback = State()

async def delete_previous_messages(chat_id: int, message_ids: list, bot: Bot):
    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception as e:
            print(f"Error deleting message {msg_id}: {str(e)}")

@router.callback_query(F.data == "feedback_menu")
async def feedback_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.delete()
    msg = await callback.message.answer(
        "Выберите действие:",
        reply_markup=keyboards.feedback_menu()
    )
    await state.set_state(FeedbackMenuStates.waiting_feedback)
    await state.update_data(messages_to_delete=[msg.message_id])
    await callback.answer()

@router.callback_query(F.data == "cancel_feedback_menu", FeedbackMenuStates.waiting_feedback)
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