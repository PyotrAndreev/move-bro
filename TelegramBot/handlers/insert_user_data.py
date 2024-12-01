import asyncio
import logging
from datetime import date
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode
import re

from ..data_base import get_db
from ..data_base import User
from sqlalchemy.orm import Session

from .. import data_base
from ..data_base import get_db
from ..keyboards import keyboards

router = Router()

class Form(StatesGroup):
    gender = State()
    first_name = State()
    second_name = State()
    email = State()
    phone = State()
    check = State()
    check_process = State()
# Тут был MainForms.blank, что это?
# Советую использовать aiogram_dialog, в нём можно легко передвигаться по стейтам(полезно, если человек хочет поменять только несколько полей в форме
@router.callback_query(F.data=="get_ready")
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    content = Text("Для начала выбери свой пол: ")
    await call.message.answer(
        **content.as_kwargs(),
        reply_markup=keyboards.gender_kb()
    )
    await state.set_state(Form.gender)

@router.callback_query(F.data=="man", Form.gender)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await state.update_data(gender="Мужчина")
    content = Text('Введите своё имя: ')
    await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(Form.first_name)

@router.callback_query(F.data=="woman", Form.gender)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await state.update_data(gender="Женщина")
    content = Text('Введите своё имя: ')
    await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(Form.first_name)

@router.message(F.text == "Назад", Form.first_name)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Для начала выбери свой пол: ")
    await message.answer(
        **content.as_kwargs(),
        reply_markup=keyboards.gender_kb()
    )
    await state.set_state(Form.gender)

@router.message(F.text, Form.first_name)
async def start_questionnaire_process(message: Message, state: FSMContext):
    if message.text.isalpha():
        await state.update_data(first_name=message.text.lower().capitalize())
        content = Text("Введите свою фамилию: ")
        await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.set_state(Form.second_name)
    else:
        await message.answer('Пожалуйста, вводите только буквы', reply_markup=keyboards.cancel_data())
        await state.set_state(Form.first_name)

@router.message(F.text == "Назад", Form.second_name)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text('Введите своё имя: ')
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(Form.first_name)

@router.message(F.text, Form.second_name)
async def start_questionnaire_process(message: Message, state: FSMContext):
    if message.text.isalpha():
        await state.update_data(second_name=message.text.lower().capitalize())
        content = Text("Введите свою почту: ")
        await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.set_state(Form.email)
    else:
        await message.answer('Пожалуйста, вводите только буквы', reply_markup=keyboards.cancel_data())
        await state.set_state(Form.second_name)

@router.message(F.text == "Назад", Form.email)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Введите свою фамилию: ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(Form.second_name)

@router.message(F.text, Form.email)
async def start_questionnaire_process(message: Message, state: FSMContext):
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message.text):
        await state.update_data(email=message.text)
        content = Text("Введите свой номер телефона в виде числа без специальных знаков: ")
        await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.set_state(Form.phone)
    else:
        await message.answer('Пожалуйста, введите корректную почту', reply_markup=keyboards.cancel_data())
        await state.set_state(Form.email)

@router.message(F.text == "Назад", Form.phone)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Введите свою почту: ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(Form.email)

@router.message(F.text, Form.phone)
async def start_questionnaire_process(message: Message, state: FSMContext):
    if message.text.isdigit() and len(message.text) <= 17:
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
    else:
        await message.answer('Пожалуйста, введите корректный телефон', reply_markup=keyboards.cancel_data())
        await state.set_state(Form.phone)

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
    user = data_base.User(first_name=data.get("first_name"),
                          last_name=data.get("second_name"),
                          gender=data.get("gender"),
                          email=data.get("email"),
                          phone=data.get("phone"),
                          registration_date=data.get("registration_date"),
                          telegram_id=data.get("telegram_id"))
    db.add(user)
    db.commit()
    await state.clear()
    await state.update_data(cur_user=user)
    content = Text(
        "В данный момент вы находитесь в меню заказчика."
    )
    await call.message.answer(
        **content.as_kwargs(),
        reply_markup=keyboards.user_menu()
    )
    await state.set_state(MainForms.choosing)