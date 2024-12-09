import asyncio
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode
from create_bot import bot
import re

from data_base import get_db
from data_base import User
from data_base import Package
from sqlalchemy.orm import Session
from keyboards import keyboards
from handlers.main_handler import MainForms

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
    check_check = State()

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
    if 1 <= len(message.text) <= 20 and message.text.isnumeric():
        await state.update_data(shipping_postal_code=message.text)
        await bot.delete_message(chat_id=message.chat.id, message_id=data.get("from_place_bot_message"))
        content = Text("Данные по месту назначения")
        place = await message.answer(**content.as_kwargs(), reply_markup=None)
        await state.update_data(to_place_bot_message=place.message_id)
        content = Text("Введите страну: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_delivery_country_bot_message=bot_message.message_id)
        await state.set_state(Form.delivery_country)
    elif message.text.isnumeric():
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
    if 1 <= len(message.text) <= 20 and message.text.isnumeric():
        await state.update_data(delivery_postal_code=message.text)
        await bot.delete_message(chat_id=message.chat.id, message_id=data.get("to_place_bot_message"))
        content = Text("Введите имя получателя: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
        await state.update_data(choose_rec_name_bot_message=bot_message.message_id)
        await state.set_state(Form.rec_name)
    elif message.text.isnumeric():
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
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_rec_name_bot_message"))
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
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_rec_email_bot_message"))
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("note_bot_message"))
    content = Text("Введите имя получателя: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_data())
    await state.update_data(choose_rec_name_bot_message=bot_message.message_id)
    await state.set_state(Form.rec_name)

@router.callback_query(F.data=="skip", Form.rec_email)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await state.update_data(rec_email=None)
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_rec_email_bot_message"))
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
        content = Text("Введите номер телефона получателя в формате +79999999999: ")
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
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_rec_phone_bot_message"))
    content = Text("Введите почту получателя в формате your_mail_name@domain.ru: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.update_data(choose_rec_email_bot_message=bot_message.message_id)
    await state.set_state(Form.rec_email)

@router.callback_query(F.data=="skip", Form.rec_phone)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    await state.update_data(rec_phone=None)
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_rec_phone_bot_message"))
    content = Text("Введите телеграм получателя: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.update_data(choose_rec_telegram_bot_message=bot_message.message_id)
    await state.set_state(Form.rec_telegram_id)

@router.message(F.text, Form.rec_phone)
async def start_questionnaire_process(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_rec_phone_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if re.match(r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$', message.text):
        await state.update_data(rec_phone=int(message.text))
        content = Text("Телеграм получателя: ")
        bot_message = await message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
        await state.update_data(choose_rec_telegram_bot_message=bot_message.message_id)
        await state.set_state(Form.rec_telegram_id)
    else:
        bot_message = await message.answer('Пожалуйста, введите корректный телефон', reply_markup=keyboards.cancel_and_skip_data())
        await state.update_data(choose_rec_phone_bot_message=bot_message.message_id)
        await state.set_state(Form.rec_phone)

@router.callback_query(F.data=="cancel", Form.rec_telegram_id)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_rec_telegram_bot_message"))
    content = Text("Введите номер телефона получателя в виде числа без специальных знаков: ")
    bot_message = await call.message.answer(**content.as_kwargs(), reply_markup=keyboards.cancel_and_skip_data())
    await state.update_data(choose_rec_phone_bot_message=bot_message.message_id)
    await state.set_state(Form.rec_phone)

@router.callback_query(F.data=="skip", Form.rec_telegram_id)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_rec_telegram_bot_message"))
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("note_bot_message"))
    await state.update_data(rec_telegram_id=None)
    content = f'Все данные заполнены!\n' \
              f'Пожалуйста, проверьте все ли верно: \n' \
              f'<b>Вес посылки</b>: {data.get("weight")} кг\n' \
              f'<b>Длина посылки</b>: {data.get("length")} см\n' \
              f'<b>Ширина посылки</b>: {data.get("width")} см\n' \
              f'<b>Высота посылки</b>: {data.get("height")} см\n' \
              f'<b>Цена доставки</b>: {data.get("cost")} руб\n' \
              f'<b>Страна отправителя</b>: {data.get("shipping_country")}\n' \
              f'<b>Штат отправителя</b>: {"" if data.get("shipping_state") is None else data.get("shipping_state")}\n' \
              f'<b>Город отправителя</b>: {data.get("shipping_city")}\n' \
              f'<b>Улица отправителя</b>: {data.get("shipping_street")}\n' \
              f'<b>Дом отправителя</b>: {data.get("shipping_house")}\n' \
              f'<b>Почтовый индекс отправителя</b>: {data.get("shipping_postal_code")}\n' \
              f'<b>Страна получателя</b>: {data.get("delivery_country")}\n' \
              f'<b>Штат получателя</b>: {"" if data.get("delivery_state") is None else data.get("delivery_state")}\n' \
              f'<b>Город получателя</b>: {data.get("delivery_city")}\n' \
              f'<b>Улица получателя</b>: {data.get("delivery_street")}\n' \
              f'<b>Дом получателя</b>: {data.get("delivery_house")}\n' \
              f'<b>Почтовый индекс получателя</b>: {data.get("delivery_postal_code")}\n' \
              f'<b>Имя получателя</b>: {data.get("rec_name")}\n' \
              f'<b>Почта получателя</b>: {"" if data.get("rec_email") is None else data.get("rec_email")}\n' \
              f'<b>Телефон получателя</b>: {"" if data.get("rec_phone") is None else data.get("rec_phone")}\n' \
              f'<b>Телеграм получателя</b>: {"" if data.get("rec_telegram_id") is None else data.get("rec_telegram_id")}\n'
    bot_message = await call.message.answer(content, parse_mode=ParseMode.HTML, reply_markup=keyboards.check_data())
    await state.update_data(choose_check_bot_message=bot_message.message_id)
    await state.set_state(Form.check_check)

@router.message(F.text, Form.rec_telegram_id)
async def start_questionnaire_process(message: Message, state: FSMContext):
    await state.update_data(rec_telegram_id=message.text)
    data = await state.get_data()
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("choose_rec_telegram_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=data.get("note_bot_message"))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    content = f'Все данные заполнены!\n' \
              f'Пожалуйста, проверьте все ли верно: \n' \
              f'<b>Вес посылки</b>: {data.get("weight")} кг\n' \
              f'<b>Длина посылки</b>: {data.get("length")} см\n' \
              f'<b>Ширина посылки</b>: {data.get("width")} см\n' \
              f'<b>Высота посылки</b>: {data.get("height")} см\n' \
              f'<b>Цена доставки</b>: {data.get("cost")} руб\n' \
              f'<b>Страна отправителя</b>: {data.get("shipping_country")}\n' \
              f'<b>Штат отправителя</b>: {"" if data.get("shipping_state") is None else data.get("shipping_state")}\n' \
              f'<b>Город отправителя</b>: {data.get("shipping_city")}\n' \
              f'<b>Улица отправителя</b>: {data.get("shipping_street")}\n' \
              f'<b>Дом отправителя</b>: {data.get("shipping_house")}\n' \
              f'<b>Почтовый индекс отправителя</b>: {data.get("shipping_postal_code")}\n' \
              f'<b>Страна получателя</b>: {data.get("delivery_country")}\n' \
              f'<b>Штат получателя</b>: {"" if data.get("delivery_state") is None else data.get("delivery_state")}\n' \
              f'<b>Город получателя</b>: {data.get("delivery_city")}\n' \
              f'<b>Улица получателя</b>: {data.get("delivery_street")}\n' \
              f'<b>Дом получателя</b>: {data.get("delivery_house")}\n' \
              f'<b>Почтовый индекс получателя</b>: {data.get("delivery_postal_code")}\n' \
              f'<b>Имя получателя</b>: {data.get("rec_name")}\n' \
              f'<b>Почта получателя</b>: {"" if data.get("rec_email") is None else data.get("rec_email")}\n' \
              f'<b>Телефон получателя</b>: {"" if data.get("rec_phone") is None else data.get("rec_phone")}\n' \
              f'<b>Телеграм получателя</b>: {"" if data.get("rec_telegram_id") is None else data.get("rec_telegram_id")}\n'
    bot_message = await message.answer(content, parse_mode=ParseMode.HTML, reply_markup=keyboards.check_data())
    await state.update_data(choose_check_bot_message=bot_message.message_id)
    await state.set_state(Form.check_check)

@router.callback_query(F.data == "incorrect", Form.check_check)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_check_bot_message"))
    content = Text("Введите вес посылки (кг): ")
    bot_message = await call.message.answer(**content.as_kwargs())
    await state.update_data(choose_weight_bot_message=bot_message.message_id)
    await state.set_state(Form.weight)

@router.callback_query(F.data == "correct", Form.check_check)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=data.get("choose_check_bot_message"))
    db: Session = next(get_db())
    user = db.query(User).filter(User.user_id == data.get("user_id")).first()
    package = Package(user=user,
                      recipient_name=data.get("rec_name"),
                      recipient_email=data.get("rec_email"),
                      recipient_phone=data.get("rec_phone"),
                      recipient_telegram_id=data.get("rec_telegram_id"),
                      weight=data.get("weight"),
                      length=data.get("length"),
                      width=data.get("width"),
                      height=data.get("height"),
                      cost=data.get("cost"),
                      shipping_country=data.get("shipping_country"),
                      shipping_state=data.get("shipping_state"),
                      shipping_city=data.get("shipping_city"),
                      shipping_street=data.get("shipping_street"),
                      shipping_house=data.get("shipping_house"),
                      shipping_postal_code=data.get("shipping_postal_code"),
                      delivery_country=data.get("delivery_country"),
                      delivery_state=data.get("delivery_state"),
                      delivery_city=data.get("delivery_city"),
                      delivery_street=data.get("delivery_street"),
                      delivery_house=data.get("delivery_house"),
                      delivery_postal_code=data.get("delivery_postal_code"))
    db.add(package)
    db.commit()
    db.expunge_all()
    bot_message = await call.message.answer('Заявка успешно создана!')
    await asyncio.sleep(2)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=bot_message.message_id)
    content = Text("Меню заказчика:")
    bot_message = await call.message.answer(
        **content.as_kwargs(),
        reply_markup=keyboards.user_menu()
    )
    await state.update_data(menu_bot_message=bot_message.message_id)
    await state.set_state(MainForms.choosing)