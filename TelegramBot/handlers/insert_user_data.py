import asyncio
import datetime
from datetime import date
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode

from TelegramBot import data_base
from TelegramBot.create_bot import bot
import re

from TelegramBot.data_base import get_db
from TelegramBot.data_base import User
from sqlalchemy.orm import Session

from TelegramBot.data_base import get_db
from TelegramBot.keyboards import keyboards
from TelegramBot.handlers.main_handler import MainForms
from TelegramBot.logging_helper import set_info_log

router = Router()

class Form(StatesGroup):
    gender = State()
    first_name = State()
    second_name = State()
    email = State()
    phone = State()
    check = State()
    check_process = State()

@router.callback_query(F.data=="get_ready", MainForms.blank)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("start_registration_bot_message"))
    content = Text("Для начала выбери свой пол: ")
    bot_message = await call.message.answer(
        **content.as_kwargs(),
        reply_markup=keyboards.gender_kb()
    )
    await state.update_data(choose_gender_bot_message=bot_message.message_id)
    await state.set_state(Form.gender)

@router.message(F.text, MainForms.blank)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.callback_query(F.data=="man", Form.gender)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_gender_bot_message"))
    await state.update_data(gender="Мужчина")
    content = Text('Введите своё имя: ')
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_name_bot_message=bot_message.message_id)
    await state.set_state(Form.first_name)

@router.callback_query(F.data=="woman", Form.gender)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_gender_bot_message"))
    await state.update_data(gender="Женщина")
    content = Text('Введите своё имя: ')
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_name_bot_message=bot_message.message_id)
    await state.set_state(Form.first_name)

@router.message(F.text, Form.gender)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@router.callback_query(F.data=="cancel", Form.first_name)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_name_bot_message"))
    content = Text("Для начала выбери свой пол: ")
    bot_message = await call.message.answer(
        **content.as_kwargs(),
        reply_markup=keyboards.gender_kb()
    )
    await state.update_data(choose_gender_bot_message=bot_message.message_id)
    await state.set_state(Form.gender)

@router.message(F.text, Form.first_name)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_name_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if message.text.isalpha() and 2 <= len(message.text) <= 20:
        await state.update_data(first_name=message.text.lower().capitalize())
        content = Text("Введите свою фамилию: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_surname_bot_message=bot_message.message_id)
        await state.set_state(Form.second_name)
    elif message.text.isalpha():
        bot_message = await message.answer('Пожалуйста, введите от 2 до 20 букв', reply_markup=keyboards.cancel_data())
        await state.update_data(choose_name_bot_message=bot_message.message_id)
        await state.set_state(Form.first_name)
    else:
        bot_message = await message.answer('Пожалуйста, вводите только буквы', reply_markup=keyboards.cancel_data())
        await state.update_data(choose_name_bot_message=bot_message.message_id)
        await state.set_state(Form.first_name)

@router.callback_query(F.data=="cancel", Form.second_name)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_surname_bot_message"))
    content = Text('Введите своё имя: ')
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_name_bot_message=bot_message.message_id)
    await state.set_state(Form.first_name)

@router.message(F.text, Form.second_name)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_surname_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if message.text.isalpha() and 2 <= len(message.text) <= 40:
        await state.update_data(second_name=message.text.lower().capitalize())
        content = Text("Введите свою почту в формате your_mail_name@domain.ru: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_mail_bot_message=bot_message.message_id)
        await state.set_state(Form.email)
    elif message.text.isalpha():
        bot_message = await message.answer('Пожалуйста, введите от 2 до 40 букв', reply_markup=keyboards.cancel_data())
        await state.update_data(choose_surname_bot_message=bot_message.message_id)
        await state.set_state(Form.second_name)
    else:
        bot_message = await message.answer('Пожалуйста, вводите только буквы', reply_markup=keyboards.cancel_data())
        await state.update_data(choose_surname_bot_message=bot_message.message_id)
        await state.set_state(Form.second_name)

@router.callback_query(F.data=="cancel", Form.email)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_mail_bot_message"))
    content = Text("Введите свою фамилию: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_surname_bot_message=bot_message.message_id)
    await state.set_state(Form.second_name)

@router.message(F.text, Form.email)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_mail_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message.text):
        await state.update_data(email=message.text)
        content = Text("Введите свой номер телефона в формате +79999999999: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_phone_bot_message=bot_message.message_id)
        await state.set_state(Form.phone)
    else:
        bot_message = await message.answer('Пожалуйста, введите корректную почту в формате your_mail_name@domain.ru', reply_markup=keyboards.cancel_data())
        await state.update_data(choose_mail_bot_message=bot_message.message_id)
        await state.set_state(Form.email)

@router.callback_query(F.data=="cancel", Form.phone)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_phone_bot_message"))
    content = Text("Введите свою почту в формате your_mail_name@domain.ru: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_mail_bot_message=bot_message.message_id)
    await state.set_state(Form.email)

@router.message(F.text, Form.phone)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_phone_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if re.match(r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$', message.text):
        await state.update_data(phone=message.text)
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
        bot_message = await message.answer(content, parse_mode=ParseMode.HTML, reply_markup=keyboards.check_data())
        await state.update_data(result_bot_message=bot_message.message_id)
        await state.set_state(Form.check_process)
    else:
        bot_message = await message.answer('Пожалуйста, введите корректный телефон  в формате +79999999999',
                                           reply_markup=keyboards.cancel_data())
        await state.update_data(choose_phone_bot_message=bot_message.message_id)
        await state.set_state(Form.phone)

@router.callback_query(F.data == 'incorrect', Form.check_process)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("result_bot_message"))
    content = Text("Для начала выбери свой пол: ")
    bot_message = await call.message.answer(
        **content.as_kwargs(),
        reply_markup=keyboards.gender_kb()
    )
    await state.update_data(choose_gender_bot_message=bot_message.message_id)
    await state.set_state(Form.gender)

@router.callback_query(F.data == 'correct', Form.check_process)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("result_bot_message"))
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
    user_id = db.query(User).filter(User.telegram_id == call.from_user.id).first().user_id
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

    set_info_log(db, data.get("telegram_id"), user_id, "Пользователь зарегистрировался в боте")

@router.message(F.text, Form.check_process)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)