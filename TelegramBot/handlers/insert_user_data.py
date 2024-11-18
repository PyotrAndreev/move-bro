import asyncio
import logging
from datetime import date
from config import config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Bold, Text
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode

from data_base import get_db
from data_base import User
from sqlalchemy.orm import Session
from keyboards import keyboards

router = Router()

class Form(StatesGroup):
    gender = State()
    first_name = State()
    second_name = State()
    email = State()
    phone = State()
    check = State()
    check_process = State()

@router.callback_query(F.data=="get_ready")
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    content = Text("Для начала выбери свой пол: ")
    await call.message.answer(
        **content.as_kwargs(),
        reply_markup=keyboards.gender_kb()
    )
    await state.set_state(Form.gender)

@router.message((F.text == "Мужчина") | (F.text == "Женщина"), Form.gender)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(gender=message.text)
    content = Text('Введите своё имя: ')
    await message.answer(**content.as_kwargs(), reply_markup=None)
    await state.set_state(Form.first_name)

@router.message(F.text, Form.gender)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, выбери вариант из тех что в клавиатуре: ', reply_markup=keyboards.gender_kb())
    await state.set_state(Form.gender)

@router.message(F.text, Form.first_name)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    content = Text("Введите свою фамилию: ")
    await message.answer(**content.as_kwargs())
    await state.set_state(Form.second_name)

@router.message(F.text, Form.second_name)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(second_name=message.text)
    content = Text("Введите свою почту: ")
    await message.answer(**content.as_kwargs())
    await state.set_state(Form.email)

@router.message(F.text, Form.email)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    content = Text("Введите свой номер телефона: ")
    await message.answer(**content.as_kwargs())
    await state.set_state(Form.phone)

@router.message(F.text, Form.phone)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(phone=int(message.text))
    await state.update_data(registration_date=date.today())
    await state.update_data(telegram_id=message.from_user.id)
    data = await state.get_data()
    content = f'Все данные заполнены!\n' \
              f'Пожалуйста, проверьте все ли верно: \n' \
              f'<b>Пол</b>: {data.get("gender")}\n' \
              f'<b>Имя</b>: {data.get("first_name")}\n' \
              f'<b>Фамилимя</b>: {data.get("second_name")}\n' \
              f'<b>Почта</b>: {data.get("email")}\n' \
              f'<b>Телефон</b>: {data.get("phone")}'
    await message.answer(content, parse_mode=ParseMode.HTML, reply_markup=keyboards.check_data())
    await state.set_state(Form.check_process)

@router.callback_query(F.data == 'incorrect', Form.check_process)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await call.answer('Запускаем сценарий с начала')
    await call.message.edit_reply_markup(reply_markup=None)
    content = Text("Для начала выбери свой пол: ")
    await call.message.answer(
        **content.as_kwargs(),
        reply_markup=keyboards.gender_kb()
    )
    await state.set_state(Form.gender)

@router.callback_query(F.data == 'correct', Form.check_process)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer('Благодарю за регистрацию. Ваши данные успешно сохранены!')
    db: Session = next(get_db())
    data = await state.get_data()
    user = User(first_name=data.get("first_name"),
                last_name=data.get("second_name"),
                gender=data.get("gender"),
                email=data.get("email"),
                phone=data.get("phone"),
                registration_date=data.get("registration_date"),
                telegram_id=data.get("telegram_id"))
    db.add(user)
    db.commit()
    await state.clear()