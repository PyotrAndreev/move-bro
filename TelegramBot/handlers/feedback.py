#feedback.py
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session
import asyncio

from TelegramBot.data_base import Logging, User, get_db
from TelegramBot.keyboards import keyboards  # Импорт клавиатур
from datetime import datetime

router = Router()


class FeedbackStates(StatesGroup):
    waiting_feedback = State()


async def delete_previous_messages(chat_id: int, message_ids: list, bot: Bot):
    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id, msg_id)
        except Exception as e:
            print(f"Error deleting message {msg_id}: {str(e)}")


@router.callback_query(F.data == "feedback")
async def feedback_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.delete()
    msg = await callback.message.answer(
        "📝 Пожалуйста, опишите вашу проблему:",
        reply_markup=keyboards.feedback_cancel_kb()
    )
    await state.set_state(FeedbackStates.waiting_feedback)
    await state.update_data(messages_to_delete=[msg.message_id])
    await callback.answer()


@router.callback_query(F.data == "cancel_feedback", FeedbackStates.waiting_feedback)
async def cancel_feedback(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
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


@router.message(FeedbackStates.waiting_feedback)
async def handle_feedback(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])

    try:
        await delete_previous_messages(message.chat.id, messages_to_delete, bot)

        # Удаляем сообщение пользователя
        try:
            await message.delete()
        except Exception as delete_error:
            print(f"Не удалось удалить сообщение: {delete_error}")

        db: Session = next(get_db())
        feedback_text = message.text

        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        if not user:
            await message.answer("❌ Ошибка: пользователь не найден")
            return

        new_feedback = Logging(
            log_type="feedback",
            log_date=datetime.now(),
            user_telegram_id=message.from_user.id,
            user_id=user.user_id,
            log_text=feedback_text
        )

        db.add(new_feedback)
        db.commit()

        # Отправляем и удаляем подтверждение
        msg = await message.answer("✅ Вопрос отправлен!")
        await asyncio.sleep(3)
        await msg.delete()

        # Главное меню
        await message.answer(
            "Меню заказчика:",
            reply_markup=keyboards.user_menu()
        )

    except Exception as e:
        # Удаляем сообщение пользователя при ошибке
        try:
            await message.delete()
        except Exception as delete_error:
            print(f"Не удалось удалить сообщение: {delete_error}")

        db.rollback()
        error_msg = await message.answer("⚠️ Произошла ошибка при сохранении отзыва")
        await asyncio.sleep(3)
        await error_msg.delete()

        await message.answer(
            "Меню заказчика:",
            reply_markup=keyboards.user_menu()
        )

    finally:
        db.close()
        await state.clear()