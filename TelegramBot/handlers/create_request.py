import asyncio
import logging
from datetime import date
from TelegramBot.config import config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Bold, Text
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode
from TelegramBot.create_bot import bot
import re

from TelegramBot.data_base import get_db
from TelegramBot.data_base import User
from TelegramBot.data_base import Package
from sqlalchemy.orm import Session
from TelegramBot.keyboards import keyboards
from TelegramBot.handlers.main_handler import MainForms

router = Router()

class Form(StatesGroup):
    weight = State()
    length = State()
    width = State()
    height = State()
    cost = State()
    shipping_country = State()
    shipping_state = State()
    shipping_city = State()
    shipping_street = State()
    shipping_house = State()
    shipping_postal_code = State()
    delivery_country = State()
    delivery_state = State()
    delivery_city = State()
    delivery_street = State()
    delivery_house = State()
    delivery_postal_code = State()
    rec_name = State()
    rec_email = State()
    rec_phone = State()
    rec_telegram_id = State()
    comment = State()
    check_process = State()

@router.callback_query(F.data=="create_request", MainForms.choosing)
async def start_request_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("menu_bot_message"))
    content = Text("Введите вес посылки (кг): ")
    bot_message = await call.message.answer(**content.as_kwargs())
    await state.update_data(choose_weight_bot_message=bot_message.message_id)
    await state.set_state(Form.weight)

@router.message(F.text, Form.weight)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_weight_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)
        content = Text("Введите размер посылки в длину (см): ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_length_bot_message=bot_message.message_id)
        await state.set_state(Form.length)
    except:
        bot_message = await message.answer('Пожалуйста, введите корректный вес')
        await state.update_data(choose_weight_bot_message=bot_message.message_id)
        await state.set_state(Form.weight)

@router.callback_query(F.data=="cancel", Form.length)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_length_bot_message"))
    content = Text("Введите вес посылки (кг): ")
    bot_message = await call.message.answer(**content.as_kwargs())
    await state.update_data(choose_weight_bot_message=bot_message.message_id)
    await state.set_state(Form.weight)

@router.message(F.text, Form.length)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_length_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    try:
        length = float(message.text)
        await state.update_data(length=length)
        content = Text("Введите размер посылки в ширину (см): ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_width_bot_message=bot_message.message_id)
        await state.set_state(Form.width)
    except:
        bot_message = await message.answer('Пожалуйста, введите корректную длину')
        await state.update_data(choose_length_bot_message=bot_message.message_id)
        await state.set_state(Form.length)

@router.callback_query(F.data=="cancel", Form.width)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_width_bot_message"))
    content = Text("Введите размер посылки в длину (см): ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_length_bot_message=bot_message.message_id)
    await state.set_state(Form.length)

@router.message(F.text, Form.width)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_width_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    try:
        width = float(message.text)
        await state.update_data(width=width)
        content = Text("Введите размер посылки в высоту (см): ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_height_bot_message=bot_message.message_id)
        await state.set_state(Form.height)
    except:
        bot_message = await message.answer('Пожалуйста, введите корректную ширину')
        await state.update_data(choose_width_bot_message=bot_message.message_id)
        await state.set_state(Form.width)

@router.callback_query(F.data=="cancel", Form.height)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_height_bot_message"))
    content = Text("Введите размер посылки в ширину (см): ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_width_bot_message=bot_message.message_id)
    await state.set_state(Form.width)

@router.message(F.text, Form.height)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_height_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    try:
        height = float(message.text)
        await state.update_data(height=height)
        content = Text("Введите цену доставки (руб): ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_cost_bot_message=bot_message.message_id)
        await state.set_state(Form.cost)
    except:
        bot_message = await message.answer('Пожалуйста, введите корректную высоту')
        await state.update_data(choose_height_bot_message=bot_message.message_id)
        await state.set_state(Form.height)

@router.callback_query(F.data=="cancel", Form.cost)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_cost_bot_message"))
    content = Text("Введите размер посылки в высоту (см): ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_height_bot_message=bot_message.message_id)
    await state.set_state(Form.height)

@router.message(F.text, Form.cost)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_cost_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    try:
        cost = float(message.text)
        await state.update_data(cost=cost)
        content = Text("Данные по месту отправки")
        place = await message.answer(**content.as_kwargs(), reply_markup=None)
        await state.update_data(from_place_bot_message=place.message_id)
        content = Text("Введите страну: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_shipping_country_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_country)
    except:
        bot_message = await message.answer('Пожалуйста, введите корректную цену')
        await state.update_data(choose_cost_bot_message=bot_message.message_id)
        await state.set_state(Form.cost)

@router.callback_query(F.data=="cancel", Form.shipping_country)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_shipping_country_bot_message"))
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("from_place_bot_message"))
    content = Text("Введите цену доставки (руб): ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_cost_bot_message=bot_message.message_id)
    await state.set_state(Form.cost)

@router.message(F.text, Form.shipping_country)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_shipping_country_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if 2 <= len(message.text) <= 40:
        await state.update_data(shipping_country=message.text)
        content = Text("Введите штат/область/округ(и т.д.): ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
        await state.update_data(choose_shipping_state_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_state)
    else:
        bot_message = await message.answer('Пожалуйста, введите от 2 до 40 символов')
        await state.update_data(choose_shipping_country_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_country)

@router.callback_query(F.data=="cancel", Form.shipping_state)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_shipping_state_bot_message"))
    content = Text("Введите страну: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_shipping_country_bot_message=bot_message.message_id)
    await state.set_state(Form.shipping_country)

@router.callback_query(F.data=="skip", Form.shipping_state)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_shipping_state_bot_message"))
    await state.update_data(shipping_state=None)
    content = Text("Введите город: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_shipping_city_bot_message=bot_message.message_id)
    await state.set_state(Form.shipping_city)

@router.message(F.text, Form.shipping_state)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_shipping_state_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if 2 <= len(message.text) <= 40:
        await state.update_data(shipping_state=message.text)
        content = Text("Введите город: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_shipping_city_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_city)
    else:
        bot_message = await message.answer('Пожалуйста, введите от 2 до 40 символов')
        await state.update_data(choose_shipping_state_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_state)

@router.callback_query(F.data=="cancel", Form.shipping_city)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_shipping_city_bot_message"))
    content = Text("Введите штат/область/округ(и т.д.): ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.update_data(choose_shipping_state_bot_message=bot_message.message_id)
    await state.set_state(Form.shipping_state)

@router.message(F.text, Form.shipping_city)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_shipping_city_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if 2 <= len(message.text) <= 40:
        await state.update_data(shipping_city=message.text)
        content = Text("Введите улицу: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_shipping_street_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_street)
    else:
        bot_message = await message.answer('Пожалуйста, введите от 2 до 40 символов')
        await state.update_data(choose_shipping_city_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_city)

@router.callback_query(F.data=="cancel", Form.shipping_street)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_shipping_street_bot_message"))
    content = Text("Введите город: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_shipping_city_bot_message=bot_message.message_id)
    await state.set_state(Form.shipping_city)

@router.message(F.text, Form.shipping_street)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_shipping_street_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if 2 <= len(message.text) <= 40:
        await state.update_data(shipping_street=message.text)
        content = Text("Введите дом: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_shipping_house_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_house)
    else:
        bot_message = await message.answer('Пожалуйста, введите от 2 до 40 символов')
        await state.update_data(choose_shipping_street_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_street)

@router.callback_query(F.data=="cancel", Form.shipping_house)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_shipping_house_bot_message"))
    content = Text("Введите улицу: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_shipping_street_bot_message=bot_message.message_id)
    await state.set_state(Form.shipping_street)

@router.message(F.text, Form.shipping_house)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_shipping_house_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if 1 <= len(message.text) <= 40:
        await state.update_data(shipping_house=message.text)
        content = Text("Введите почтовый индекс: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_shipping_postal_code_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_postal_code)
    else:
        bot_message = await message.answer('Пожалуйста, введите от 1 до 40 символов')
        await state.update_data(choose_shipping_house_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_house)

@router.callback_query(F.data=="cancel", Form.shipping_postal_code)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_shipping_postal_code_bot_message"))
    content = Text("Введите дом: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_shipping_house_bot_message=bot_message.message_id)
    await state.set_state(Form.shipping_house)

@router.message(F.text, Form.shipping_postal_code)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_shipping_postal_code_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if 1 <= len(message.text) <= 20 and message.text.isalpha():
        await state.update_data(shipping_postal_code=message.text)
        await bot.delete_message(chat_id=message.chat.id, message_id=data.get("from_place_bot_message"))
        content = Text("Данные по месту назначения")
        place = await message.answer(**content.as_kwargs(), reply_markup=None)
        await state.update_data(to_place_bot_message=place.message_id)
        content = Text("Введите страну: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_delivery_country_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_country)
    elif message.text.isalpha():
        bot_message = await message.answer('Пожалуйста, введите от 1 до 20 символов')
        await state.update_data(choose_shipping_postal_code_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_postal_code)
    else:
        bot_message = await message.answer('Пожалуйста, вводите только цифры')
        await state.update_data(choose_shipping_postal_code_bot_message=bot_message.message_id)
        await state.set_state(Form.shipping_postal_code)

@router.callback_query(F.data=="cancel", Form.delivery_country)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_delivery_country_bot_message"))
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("to_place_bot_message"))
    content = Text("Данные по месту отправки")
    place = await call.message.answer(**content.as_kwargs(), reply_markup=None)
    await state.update_data(from_place_bot_message=place.message_id)
    content = Text("Введите почтовый индекс: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_shipping_postal_code_bot_message=bot_message.message_id)
    await state.set_state(Form.shipping_postal_code)

@router.message(F.text, Form.delivery_country)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_delivery_country_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if 2 <= len(message.text) <= 40:
        await state.update_data(delivery_country=message.text)
        content = Text("Введите штат/область/округ(и т.д.): ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
        await state.update_data(choose_delivery_state_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_state)
    else:
        bot_message = await message.answer('Пожалуйста, введите от 2 до 40 символов')
        await state.update_data(choose_delivery_country_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_country)

@router.callback_query(F.data=="cancel", Form.delivery_state)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_delivery_state_bot_message"))
    content = Text("Введите страну: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_delivery_country_bot_message=bot_message.message_id)
    await state.set_state(Form.delivery_country)

@router.callback_query(F.data=="skip", Form.delivery_state)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_delivery_state_bot_message"))
    await state.update_data(delivery_state=None)
    content = Text("Введите город: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_delivery_city_bot_message=bot_message.message_id)
    await state.set_state(Form.delivery_city)

@router.message(F.text, Form.delivery_state)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_delivery_state_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if 2 <= len(message.text) <= 40:
        await state.update_data(delivery_state=message.text)
        content = Text("Введите город: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_delivery_city_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_city)
    else:
        bot_message = await message.answer('Пожалуйста, введите от 2 до 40 символов')
        await state.update_data(choose_delivery_state_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_state)

@router.callback_query(F.data=="cancel", Form.delivery_city)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_delivery_city_bot_message"))
    content = Text("Введите штат/область/округ(и т.д.): ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.update_data(choose_delivery_state_bot_message=bot_message.message_id)
    await state.set_state(Form.delivery_state)

@router.message(F.text, Form.delivery_city)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_delivery_city_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if 2 <= len(message.text) <= 40:
        await state.update_data(delivery_city=message.text)
        content = Text("Введите улицу: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_delivery_street_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_street)
    else:
        bot_message = await message.answer('Пожалуйста, введите от 2 до 40 символов')
        await state.update_data(choose_delivery_city_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_city)

@router.callback_query(F.data=="cancel", Form.delivery_street)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_delivery_street_bot_message"))
    content = Text("Введите город: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_delivery_city_bot_message=bot_message.message_id)
    await state.set_state(Form.delivery_city)

@router.message(F.text, Form.delivery_street)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_delivery_street_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if 2 <= len(message.text) <= 40:
        await state.update_data(delivery_street=message.text)
        content = Text("Введите дом: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_delivery_house_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_house)
    else:
        bot_message = await message.answer('Пожалуйста, введите от 2 до 40 символов')
        await state.update_data(choose_delivery_street_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_street)

@router.callback_query(F.data=="cancel", Form.delivery_house)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_delivery_house_bot_message"))
    content = Text("Введите улицу: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_delivery_street_bot_message=bot_message.message_id)
    await state.set_state(Form.delivery_street)

@router.message(F.text, Form.delivery_house)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_delivery_house_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if 1 <= len(message.text) <= 40:
        await state.update_data(delivery_house=message.text)
        content = Text("Введите почтовый индекс: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_delivery_postal_code_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_postal_code)
    else:
        bot_message = await message.answer('Пожалуйста, введите от 1 до 40 символов')
        await state.update_data(choose_delivery_house_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_house)

@router.callback_query(F.data=="cancel", Form.delivery_postal_code)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_delivery_postal_code_bot_message"))
    content = Text("Введите дом: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_delivery_house_bot_message=bot_message.message_id)
    await state.set_state(Form.delivery_house)

@router.message(F.text, Form.delivery_postal_code)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_delivery_postal_code_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if 1 <= len(message.text) <= 20 and message.text.isalpha():
        await state.update_data(delivery_postal_code=message.text)
        await bot.delete_message(chat_id=message.chat.id, message_id=data.get("to_place_bot_message"))
        content = Text("Введите имя получателя: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_rec_name_bot_message=bot_message.message_id)
        await state.set_state(Form.rec_name)
    elif message.text.isalpha():
        bot_message = await message.answer('Пожалуйста, введите от 1 до 20 символов')
        await state.update_data(choose_delivery_postal_code_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_postal_code)
    else:
        bot_message = await message.answer('Пожалуйста, вводите только цифры')
        await state.update_data(choose_delivery_postal_code_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_postal_code)

@router.callback_query(F.data=="cancel", Form.rec_name)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_delivery_postal_code_bot_message"))
    content = Text("Данные по месту назначения")
    place = await call.message.answer(**content.as_kwargs(), reply_markup=None)
    await state.update_data(to_place_bot_message=place.message_id)
    content = Text("Введите почтовый индекс: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_delivery_postal_code_bot_message=bot_message.message_id)
    await state.set_state(Form.delivery_postal_code)

@router.message(F.text, Form.rec_name)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_rec_name_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if message.text.isalpha():
        await state.update_data(rec_name=message.text.lower().capitalize())
        note = await message.answer("Чтобы курьер смог связаться с получателем при возникновении проблемы, настоятельно рекомендуется заполнить хотя бы одно поле из следующих трёх: почта, телефон, телеграм")
        await state.update_data(note_bot_message=note.message_id)
        content = Text("Введите почту получателя в формате your_mail_name@domain.ru: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
        await state.update_data(choose_rec_email_bot_message=bot_message.message_id)
        await state.set_state(Form.rec_email)
    else:
        bot_message = await message.answer('Пожалуйста, вводите только буквы', reply_markup=keyboards.cancel_data())
        await state.update_data(choose_rec_name_bot_message=bot_message.message_id)
        await state.set_state(Form.rec_name)

@router.callback_query(F.data=="cancel", Form.rec_email)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_rec_email_code_bot_message"))
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("note_bot_message"))
    content = Text("Введите имя получателя: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_rec_name_bot_message=bot_message.message_id)
    await state.set_state(Form.rec_name)

@router.callback_query(F.data=="skip", Form.rec_email)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await state.update_data(rec_email=None)
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_rec_email_code_bot_message"))
    content = Text("Введите номер телефона получателя в формате +79999999999: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.update_data(choose_rec_phone_bot_message=bot_message.message_id)
    await state.set_state(Form.rec_phone)

@router.message(F.text, Form.rec_email)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_rec_email_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message.text):
        await state.update_data(rec_email=message.text)
        content = Text("Введите номер телефона получателя в виде числа без специальных знаков: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
        await state.update_data(choose_rec_phone_bot_message=bot_message.message_id)
        await state.set_state(Form.rec_phone)
    else:
        bot_message = await message.answer('Пожалуйста, введите корректную почту', reply_markup=keyboards.cancel_and_skip_data())
        await state.update_data(choose_rec_email_bot_message=bot_message.message_id)
        await state.set_state(Form.rec_email)

@router.callback_query(F.data=="cancel", Form.rec_phone)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_rec_phone_code_bot_message"))
    content = Text("Введите почту получателя: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.update_data(choose_rec_email_bot_message=bot_message.message_id)
    await state.set_state(Form.rec_email)

@router.callback_query(F.data=="skip", Form.rec_phone)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await state.update_data(rec_phone=None)
    content = Text("Введите телеграм получателя: ")
    await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.set_state(Form.rec_telegram_id)

@router.message(F.text, Form.rec_phone)
async def start_questionnaire_process(message: Message, state: FSMContext):
    if message.text.isdigit() and len(message.text) <= 17:
        await state.update_data(rec_phone=int(message.text))
        content = Text("Телеграм получателя: ")
        await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
        await state.set_state(Form.rec_telegram_id)
    else:
        await message.answer('Пожалуйста, введите корректный телефон', reply_markup=keyboards.cancel_and_skip_data())
        await state.set_state(Form.rec_phone)

@router.message(F.text == "Назад", Form.rec_telegram_id)
async def start_questionnaire_process(message: Message, state: FSMContext):
    content = Text("Введите номер телефона получателя в виде числа без специальных знаков: ")
    await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.set_state(Form.rec_phone)

@router.message(F.text == "Пропустить", Form.rec_telegram_id)
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
              f'<b>Телеграм получателя</b>: {"" if data.get("pec_telegram_id") is None else data.get("pec_telegram_id")}\n'
    await state.set_state(Form.check_process)
    await message.answer(content, parse_mode=ParseMode.HTML, reply_markup=keyboards.check_data())

@router.message(F.text, Form.rec_telegram_id)
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
              f'<b>Телеграм получателя</b>: {"" if data.get("pec_telegram_id") is None else data.get("pec_telegram_id")}\n'
    await state.set_state(Form.check_process)
    await message.answer(content, parse_mode=ParseMode.HTML, reply_markup=keyboards.check_data())

@router.callback_query(F.data == 'incorrect', Form.check_process)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await call.answer('Запускаем сценарий с начала')
    await call.message.edit_reply_markup(reply_markup=None)
    content = Text("Вес посылки (кг): ")
    await call.message.answer(**content.as_kwargs())
    await state.set_state(Form.weight)

@router.callback_query(F.data == 'correct', Form.check_process)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    db: Session = next(get_db())
    data = await state.get_data()
    package = Package(recipient_name=data.get("rec_name"),
                   recipient_email=data.get("rec_email"),
                   recipient_phone=data.get("rec_phone"),
                   recipient_telegram_id=data.get("pec_telegram_id"),
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
    