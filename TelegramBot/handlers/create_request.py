import asyncio
import logging
from datetime import date
from ..config import config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Bold, Text
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode
import re

from ..data_base import get_db
from ..data_base import User
from ..data_base import Package
from sqlalchemy.orm import Session
from ..keyboards import keyboards
from ..handlers.main_handler import MainForms

router = Router()

class RequestForm(StatesGroup):
    weight = State()
    length = State()
    width = State()
    height = State()
    cost = State()
    shipping_address = State()
    delivery_address = State()
    rec_name = State()
    rec_email = State()
    rec_phone = State()
    rec_telegram_id = State()
    comment = State()
    check_process = State() # Поменяй название стейта, у тебя такое же в регистрации. А лучше измени название стейт группы. Я поменял для работоспособности, не забудь поменять потом)

@router.message(F.text == "Создать заявку на отправку", MainForms.choosing)
async def start_request_process(message: Message, state: FSMContext):
    content = Text("Вес посылки (кг): ")
    await message.answer(**content.as_kwargs())
    await state.set_state(RequestForm.weight)

@router.message(F.text, RequestForm.weight)
async def start_questionnaire_process(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)
        content = Text("Размер посылки в длину (см): ")
        await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.set_state(RequestForm.length)
    except:
        await message.answer('Пожалуйста, введите корректный вес')
        await state.set_state(RequestForm.weight)

@router.message(F.text == "Назад", RequestForm.length)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Вес посылки (кг): ")
    await message.answer(**content.as_kwargs())
    await state.set_state(RequestForm.weight)

@router.message(F.text, RequestForm.length)
async def start_questionnaire_process(message: Message, state: FSMContext):
    try:
        length = float(message.text)
        await state.update_data(length=length)
        content = Text("Размер посылки в ширину (см): ")
        await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.set_state(RequestForm.width)
    except:
        await message.answer('Пожалуйста, введите корректную длину')
        await state.set_state(RequestForm.length)

@router.message(F.text == "Назад", RequestForm.width)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Размер посылки в длину (см): ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(RequestForm.length)

@router.message(F.text, RequestForm.width)
async def start_questionnaire_process(message: Message, state: FSMContext):
    try:
        width = float(message.text)
        await state.update_data(width=width)
        content = Text("Размер посылки в высоту (см): ")
        await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.set_state(RequestForm.height)
    except:
        await message.answer('Пожалуйста, введите корректную ширину')
        await state.set_state(RequestForm.width)

@router.message(F.text == "Назад", RequestForm.height)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Размер посылки в ширину (см): ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(RequestForm.width)

@router.message(F.text, RequestForm.height)
async def start_questionnaire_process(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        await state.update_data(height=height)
        content = Text("Цена доставки (руб): ")
        await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.set_state(RequestForm.cost)
    except:
        await message.answer('Пожалуйста, введите корректную высоту')
        await state.set_state(RequestForm.height)

@router.message(F.text == "Назад", RequestForm.cost)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Размер посылки в высоту (см): ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(RequestForm.height)

@router.message(F.text, RequestForm.cost)
async def start_questionnaire_process(message: Message, state: FSMContext):
    try:
        cost = float(message.text)
        await state.update_data(cost=cost)
        content = Text("Введите место отправки в виде \"улица, дом, город, почтовый индекс\"\n"
                       + "Пример: Красная площадь, 9, Москва, 1090120\n"
                       + "P.s. адрес легко можно посмотреть в Яндекс Картах")
        await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.set_state(RequestForm.shipping_address)
    except:
        await message.answer('Пожалуйста, введите корректную цену')
        await state.set_state(RequestForm.cost)

@router.message(F.text == "Назад", RequestForm.shipping_address)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Цена доставки (руб): ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(RequestForm.cost)

@router.message(F.text, RequestForm.shipping_address)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(shipping_address=message.text)
    content = Text("Введите место доставки: ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(RequestForm.delivery_address)

@router.message(F.text == "Назад", RequestForm.delivery_address)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Введите место отправки в виде \"улица, дом, город, почтовый индекс\"\n"
                       + "Пример: Красная площадь, 9, Москва, 1090120\n"
                       + "P.s. адрес легко можно посмотреть в Яндекс Картах")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(RequestForm.shipping_address)

@router.message(F.text, RequestForm.delivery_address)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(delivery_address=message.text)
    content = Text("Имя получателя: ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(RequestForm.rec_name)

@router.message(F.text == "Назад", RequestForm.rec_name)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Введите место доставки: ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(RequestForm.delivery_address)

@router.message(F.text, RequestForm.rec_name)
async def start_questionnaire_process(message: Message, state: FSMContext):
    if message.text.isalpha():
        await state.update_data(rec_name=message.text.lower().capitalize())
        await message.answer("Чтобы курьер смог связаться с получателем при возникновении проблемы, настоятельно рекомендуется заполнить хотя бы одно поле из следующих трёх: почта, телефон, телеграм")
        content = Text("Введите почту получателя: ")
        await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
        await state.set_state(RequestForm.rec_email)
    else:
        await message.answer('Пожалуйста, вводите только буквы', reply_markup=keyboards.cancel_data())
        await state.set_state(RequestForm.rec_name)

@router.message(F.text == "Назад", RequestForm.rec_email)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Имя получателя: ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.set_state(RequestForm.rec_name)

@router.message(F.text == "Пропустить", RequestForm.rec_email)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(rec_email=None)
    content = Text("Введите номер телефона получателя в виде числа без специальных знаков: ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.set_state(RequestForm.rec_phone)

@router.message(F.text, RequestForm.rec_email)
async def start_questionnaire_process(message: Message, state: FSMContext):
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message.text):
        await state.update_data(rec_email=message.text)
        content = Text("Введите номер телефона получателя в виде числа без специальных знаков: ")
        await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
        await state.set_state(RequestForm.rec_phone)
    else:
        await message.answer('Пожалуйста, введите корректную почту', reply_markup=keyboards.cancel_and_skip_data())
        await state.set_state(RequestForm.rec_email)

@router.message(F.text == "Назад", RequestForm.rec_phone)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Введите почту получателя: ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.set_state(RequestForm.rec_email)

@router.message(F.text == "Пропустить", RequestForm.rec_phone)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(rec_phone=None)
    content = Text("Телеграм получателя: ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.set_state(RequestForm.rec_telegram_id)

@router.message(F.text, RequestForm.rec_phone)
async def start_questionnaire_process(message: Message, state: FSMContext):
    if message.text.isdigit() and len(message.text) <= 17:
        await state.update_data(rec_phone=int(message.text))
        content = Text("Телеграм получателя: ")
        await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
        await state.set_state(RequestForm.rec_telegram_id)
    else:
        await message.answer('Пожалуйста, введите корректный телефон', reply_markup=keyboards.cancel_and_skip_data())
        await state.set_state(RequestForm.rec_phone)

@router.message(F.text == "Назад", RequestForm.rec_telegram_id)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Введите номер телефона получателя в виде числа без специальных знаков: ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.set_state(RequestForm.rec_phone)

@router.message(F.text == "Пропустить", RequestForm.rec_telegram_id)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(rec_telegram_id=None)
    data = await state.get_data()
    content = f'Все данные заполнены!\n' \
              f'Пожалуйста, проверьте все ли верно: \n' \
              f'<b>Вес посылки</b>: {data.get("weight")} кг\n' \
              f'<b>Длина посылки</b>: {data.get("length")} см\n' \
              f'<b>Ширина посылки</b>: {data.get("width")} см\n' \
              f'<b>Высота посылки</b>: {data.get("height")} см\n' \
              f'<b>Цена доставки</b>: {data.get("cost")} руб\n' \
              f'<b>Адрес отправки</b>: {data.get("shipping_address")}\n' \
              f'<b>Адрес доставки</b>: {data.get("delivery_address")}\n' \
              f'<b>Имя получателя</b>: {data.get("rec_name")}\n' \
              f'<b>Почта получателя</b>: {"" if data.get("rec_email") is None else data.get("rec_email")}\n' \
              f'<b>Телефон получателя</b>: {"" if data.get("rec_phone") is None else data.get("rec_phone")}\n' \
              f'<b>Телеграм получателя</b>: {"" if data.get("rec_telegram_id") is None else data.get("rec_telegram_id")}\n'
    await state.set_state(RequestForm.check_process)
    await message.answer(content, parse_mode=ParseMode.HTML, reply_markup=keyboards.check_data())

@router.message(F.text, RequestForm.rec_telegram_id)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(rec_telegram_id=message.text)
    data = await state.get_data()
    content = f'Все данные заполнены!\n' \
              f'Пожалуйста, проверьте все ли верно: \n' \
              f'<b>Вес посылки</b>: {data.get("weight")} кг\n' \
              f'<b>Длина посылки</b>: {data.get("length")} см\n' \
              f'<b>Ширина посылки</b>: {data.get("width")} см\n' \
              f'<b>Высота посылки</b>: {data.get("height")} см\n' \
              f'<b>Цена доставки</b>: {data.get("cost")} руб\n' \
              f'<b>Адрес отправки</b>: {data.get("shipping_address")}\n' \
              f'<b>Адрес доставки</b>: {data.get("delivery_address")}\n' \
              f'<b>Имя получателя</b>: {data.get("rec_name")}\n' \
              f'<b>Почта получателя</b>: {"" if data.get("rec_email") is None else data.get("rec_email")}\n' \
              f'<b>Телефон получателя</b>: {"" if data.get("rec_phone") is None else data.get("rec_phone")}\n' \
              f'<b>Телеграм получателя</b>: {"" if data.get("rec_telegram_id") is None else data.get("rec_telegram_id")}\n'
    await state.set_state(RequestForm.check_process)
    await message.answer(content, parse_mode=ParseMode.HTML, reply_markup=keyboards.check_data())

@router.callback_query(F.data == 'incorrect', RequestForm.check_process)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await call.answer('Запускаем сценарий с начала')
    await call.message.edit_reply_markup(reply_markup=None)
    content = Text("Вес посылки (кг): ")
    await call.message.answer(**content.as_kwargs())
    await state.set_state(RequestForm.weight)

@router.callback_query(F.data == 'correct', RequestForm.check_process)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    db: Session = next(get_db())
    data = await state.get_data()
    package = Package(recipient_name=data.get("rec_name"),
                   recipient_email=data.get("rec_email"),
                   recipient_phone=data.get("rec_phone"),
                   recipient_telegram_id=data.get("rec_telegram_id"),
                   weight=data.get("weight"),
                   length=data.get("length"),
                   width=data.get("width"),
                   height=data.get("height"),
                   cost=data.get("cost"),
                   shipping_address=data.get("shipping_address"),
                   delivery_address=data.get("delivery_address"))
    db.add(package)
    db.commit()
    await call.message.answer('Заявка успешно создана!')
    