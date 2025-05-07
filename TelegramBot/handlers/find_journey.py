import datetime
import re

import aiogram_dialog.api.entities.modes
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import DialogManager, Window, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Column, SwitchTo, Back, Row
from aiogram_dialog.widgets.text import Const, Format
from typing import Any

from aiogram.types import InlineKeyboardButton

from TelegramBot.data_base import get_db, Package, User, PackageNote, Courier, Courier_Request
from sqlalchemy.orm import Session
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram_dialog import Dialog, ShowMode
from TelegramBot.keyboards import keyboards
from asyncio import sleep, create_task
from TelegramBot.logging_helper import set_info_log
from TelegramBot.create_bot import bot
from TelegramBot.enum_types import *

# ==== Создаем отдельный роутер для диалогов ====
dialog_router = Router()


class FindJourneysStates(StatesGroup):
    filtering = State()
    choosing_orders = State()
    enrolling = State()
    choosing_source_city = State()
    choosing_destination_city = State()
    weight = State()
    length = State()
    width = State()
    height = State()
    cost = State()
    shipping_street = State()
    shipping_house = State()
    shipping_postal_code = State()
    delivery_street = State()
    delivery_house = State()
    delivery_postal_code = State()
    rec_name = State()
    rec_email = State()
    rec_phone = State()
    rec_telegram_id = State()
    comment = State()
    check_process = State()

async def get_form_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    return {
        "weight": data.get("weight"),
        "length": data.get("length"),
        "width": data.get("width"),
        "height": data.get("height"),
        "cost": data.get("cost"),
        "shipping_country": data.get("shipping_country"),
        "shipping_state": data.get("shipping_state"),
        "shipping_city": data.get("shipping_city"),
        "shipping_street": data.get("shipping_street"),
        "shipping_house": data.get("shipping_house"),
        "shipping_postal_code": data.get("shipping_postal_code"),
        "delivery_country": data.get("delivery_country"),
        "delivery_state": data.get("delivery_state"),
        "delivery_city": data.get("delivery_city"),
        "delivery_street": data.get("delivery_street"),
        "delivery_house": data.get("delivery_house"),
        "delivery_postal_code": data.get("delivery_postal_code"),
        "rec_name": data.get("rec_name"),
        "rec_email": data.get("rec_email"),
        "rec_phone": data.get("rec_phone"),
        "rec_telegram_id": data.get("rec_telegram_id"),
    }

async def get_safe_form_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data

    def safe_val(key):
        val = data.get(key)
        return val if val is not None else "-"
    
    return {
        "weight": safe_val("weight"),
        "length": safe_val("length"),
        "width": safe_val("width"),
        "height": safe_val("height"),
        "cost": safe_val("cost"),
        "shipping_country": safe_val("shipping_country"),
        "shipping_state": safe_val("shipping_state"),
        "shipping_city": safe_val("shipping_city"),
        "shipping_street": safe_val("shipping_street"),
        "shipping_house": safe_val("shipping_house"),
        "shipping_postal_code": safe_val("shipping_postal_code"),
        "delivery_country": safe_val("delivery_country"),
        "delivery_state": safe_val("delivery_state"),
        "delivery_city": safe_val("delivery_city"),
        "delivery_street": safe_val("delivery_street"),
        "delivery_house": safe_val("delivery_house"),
        "delivery_postal_code": safe_val("delivery_postal_code"),
        "rec_name": safe_val("rec_name"),
        "rec_email": safe_val("rec_email"),
        "rec_phone": safe_val("rec_phone"),
        "rec_telegram_id": safe_val("rec_telegram_id"),
    }


async def on_dialog_start(start_data: Any, manager: DialogManager):
    manager.dialog_data['source_city'] = "Не выбран"
    manager.dialog_data['destination_city'] = "Не выбран"


async def source_cities_getter(dialog_manager: DialogManager, **kwargs):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == dialog_manager.event.from_user.id).first()
    courier = db.query(Courier).filter(Courier.user_id == user.user_id).first()
    cities = db.query(Courier_Request.shipping_city.distinct()).filter(Courier_Request.courier_id != courier.courier_id)
    if dialog_manager.dialog_data.get('destination_city') != 'Не выбран':
        cities = cities.filter_by(delivery_city=dialog_manager.dialog_data.get('destination_city'))
    cities = cities.all()
    cities = [row[0] for row in cities]
    return {
        'source_cities': cities
    }


async def on_source_city_selected(callback: CallbackQuery, widget: Any, manager: DialogManager, item: str):
    manager.dialog_data['source_city'] = item
    await manager.switch_to(FindJourneysStates.filtering)


async def destination_cities_getter(dialog_manager: DialogManager, **kwargs):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == dialog_manager.event.from_user.id).first()
    courier = db.query(Courier).filter(Courier.user_id == user.user_id).first()
    cities = db.query(Courier_Request.delivery_city.distinct()).filter(Courier_Request.courier_id != courier.courier_id)
    if dialog_manager.dialog_data.get('source_city') != 'Не выбран':
        cities = cities.filter_by(shipping_city=dialog_manager.dialog_data.get('source_city'))
    cities = cities.all()
    cities = [row[0] for row in cities]
    return {
        'destination_cities': cities
    }


async def on_destination_city_selected(callback: CallbackQuery, widget: Any, manager: DialogManager, item: str):
    manager.dialog_data['destination_city'] = item
    await manager.switch_to(FindJourneysStates.filtering)


async def orders_getter(dialog_manager: DialogManager, **kwargs):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == dialog_manager.event.from_user.id).first()
    courier = db.query(Courier).filter(Courier.user_id == user.user_id).first()
    # requests = db.query(Courier_Request).filter(Courier_Request.courier_id != courier.courier_id)
    requests = db.query(Courier_Request)
    source_city = dialog_manager.dialog_data.get('source_city')
    destination_city = dialog_manager.dialog_data.get('destination_city')
    if source_city != 'Не выбран':
        requests = requests.filter_by(shipping_city=source_city)
    if destination_city != 'Не выбран':
        requests = requests.filter_by(delivery_city=destination_city)
    return {
        'requests': requests
    }


async def on_orders_selected(callback: CallbackQuery, widget: Any, manager: DialogManager,
                             item: int):  # item теперь строка!
    manager.dialog_data["courier_request_id"] = item  # item - это ID который мы получим
    db: Session = next(get_db())
    request = db.query(Courier_Request).filter(Courier_Request.courier_request_id == item).first()
    manager.dialog_data['request'] = request
    manager.dialog_data["shipping_country"] = request.shipping_country
    manager.dialog_data['shipping_state'] = request.shipping_state
    manager.dialog_data['shipping_city'] = request.shipping_city
    manager.dialog_data['delivery_country'] = request.delivery_country
    manager.dialog_data['delivery_state'] = request.delivery_state
    manager.dialog_data['delivery_city'] = request.delivery_city
    await manager.switch_to(FindJourneysStates.enrolling)

    # user_id = manager.event.from_user.id
    # user = db.query(User).filter(User.telegram_id == user_id).first()
    # set_info_log(db, user.telegram_id, user.user_id,
    #              f"Пользователь стал доставщиком посылки {manager.dialog_data['package']}")

async def back_to_menu(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.delete()
    await manager.done()
    await callback.message.answer(text="Меню заказчика:", reply_markup=keyboards.user_menu())

async def on_weight_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    try:
        manager.dialog_data["weight"] = float(message.text)
        await manager.next(show_mode=ShowMode.EDIT)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный вес")

async def on_length_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    try:
        manager.dialog_data["length"] = float(message.text)
        await manager.next(show_mode=ShowMode.EDIT)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную длину")

async def on_width_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    try:
        manager.dialog_data["width"] = float(message.text)
        await manager.next(show_mode=ShowMode.EDIT)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную ширину")

async def on_height_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    try:
        manager.dialog_data["height"] = float(message.text)
        await manager.next(show_mode=ShowMode.EDIT)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную высоту")

async def on_cost_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    try:
        manager.dialog_data["cost"] = float(message.text)
        await manager.next(show_mode=ShowMode.EDIT)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную цену")

async def on_shipping_street_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if 2 <= len(message.text) <= 40:
        manager.dialog_data["shipping_street"] = message.text
        await manager.next(show_mode=ShowMode.EDIT)
    else:
        await message.answer("Пожалуйста, введите от 2 до 40 символов")

async def on_shipping_house_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if 1 <= len(message.text) <= 40:
        manager.dialog_data["shipping_house"] = message.text
        await manager.next(show_mode=ShowMode.EDIT)
    else:
        await message.answer("Пожалуйста, введите от 1 до 40 символов")

async def on_shipping_postal_code_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if 1 <= len(message.text) <= 20 and message.text.isdigit():
        manager.dialog_data["shipping_postal_code"] = message.text
        await manager.next(show_mode=ShowMode.EDIT)
    elif message.text.isalpha():
        await message.answer("Пожалуйста, введите от 1 до 20 символов")
    else:
        await message.answer("Пожалуйста, вводите только цифры")

async def on_delivery_street_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if 2 <= len(message.text) <= 40:
        manager.dialog_data["delivery_street"] = message.text
        await manager.next(show_mode=ShowMode.EDIT)
    else:
        await message.answer("Пожалуйста, введите от 2 до 40 символов")

async def on_delivery_house_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if 1 <= len(message.text) <= 40:
        manager.dialog_data["delivery_house"] = message.text
        await manager.next(show_mode=ShowMode.EDIT)
    else:
        await message.answer("Пожалуйста, введите от 1 до 40 символов")

async def on_delivery_postal_code_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if 1 <= len(message.text) <= 20 and message.text.isdigit():
        manager.dialog_data["delivery_postal_code"] = message.text
        await manager.next(show_mode=ShowMode.EDIT)
    elif message.text.isalpha():
        await message.answer("Пожалуйста, введите от 1 до 20 символов")
    else:
        await message.answer("Пожалуйста, вводите только цифры")

async def on_rec_name_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    manager.dialog_data["rec_name"] = message.text.lower().capitalize()
    await manager.next(show_mode=ShowMode.EDIT)

async def on_rec_email_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if re.match(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", message.text
    ):
        manager.dialog_data["rec_email"] = message.text
        await manager.next(show_mode=ShowMode.EDIT)
    else:
        await message.answer(
            "Пожалуйста, введите корректную почту",
        )

async def on_rec_phone_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if len(message.text) <= 17:
        manager.dialog_data["rec_phone"] = int(message.text)
        await manager.next(show_mode=ShowMode.EDIT)
    else:
        await message.answer(
            "Пожалуйста, введите корректный телефон",
        )

async def on_rec_telegram_id_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    manager.dialog_data["rec_telegram_id"] = message.text
    await manager.switch_to(FindJourneysStates.check_process, show_mode=ShowMode.EDIT)

async def on_skip_rec_email(
    callback_query: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    manager.dialog_data["rec_email"] = None
    await manager.next(show_mode=ShowMode.EDIT)

async def on_skip_rec_phone(
    callback_query: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    manager.dialog_data["rec_phone"] = None
    await manager.next(show_mode=ShowMode.EDIT)

async def on_skip_rec_telegram_id(
    callback_query: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    manager.dialog_data["rec_telegram_id"] = None
    await manager.switch_to(FindJourneysStates.check_process, show_mode=ShowMode.EDIT)

async def on_restart_clicked(callback_query: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(FindJourneysStates.weight, show_mode=ShowMode.EDIT)

async def on_finish_clicked(
    callback_query: CallbackQuery, button: Button, manager: DialogManager
):
    chat_id = callback_query.message.chat.id
    await callback_query.message.delete()
    db: Session = next(get_db())
    user_tg_id = callback_query.from_user.id
    user: User = db.query(User).filter(User.telegram_id == user_tg_id).first()
    user_id = user.user_id
    data = await get_form_data(manager)
    item = manager.dialog_data["courier_request_id"]
    request = db.query(Courier_Request).filter(Courier_Request.courier_request_id == item).first()    
    package = Package(
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
        delivery_postal_code=data.get("delivery_postal_code"),
        user=user,
        courier_request=request
    )
    db.add(package)
    db.commit()

    set_info_log(db, user_tg_id, user_id, f"Создана заявка на отправку посылки {package.package_id}")

    message = await callback_query.bot.send_message(chat_id, text="Заявка успешно создана!")
    create_task(delete_message_after_time(callback_query, manager, message))
    await manager.done()
    await callback_query.bot.send_message(chat_id, text="В данный момент вы находитесь в меню заказчика.", reply_markup=keyboards.user_menu())

async def delete_message_after_time(
    callback_query: CallbackQuery, manager: DialogManager, message
):
    await sleep(5)
    try:
        await callback_query.bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass



async def magic_button(
    callback_query: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    manager.dialog_data['weight'] = 10
    manager.dialog_data['length'] = 10
    manager.dialog_data['width'] = 10
    manager.dialog_data['height'] = 10
    manager.dialog_data['cost'] = 10
    manager.dialog_data['shipping_street'] = "Kremenchugskaya"
    manager.dialog_data['shipping_postal_code'] = 423333
    manager.dialog_data['shipping_house'] = 10
    manager.dialog_data['delivery_street'] = "Nebrosko"
    manager.dialog_data['delivery_house'] = 10
    manager.dialog_data['delivery_postal_code'] = 10101
    manager.dialog_data['rec_name'] = "FreddyBear"
    manager.dialog_data['rec_email'] = "freddy@scottgames.io"
    manager.dialog_data['rec_phone'] = "12345678910"
    manager.dialog_data['rec_telegram_id'] = "@freddy_pizzaman"
    await manager.switch_to(FindJourneysStates.check_process, show_mode=ShowMode.EDIT)





filtering = Window(
    Const('Настройте фильтры(при необходимости), после чего нажмите кнопку: "Маршруты"'),
    Column(
        SwitchTo(text=Format("Город отправки: {dialog_data[source_city]}"), state=FindJourneysStates.choosing_source_city,
                 id="source_city"),
        SwitchTo(text=Format("Город доставки: {dialog_data[destination_city]}"),
                 state=FindJourneysStates.choosing_destination_city, id="destination_city"),
        SwitchTo(text=Const('Маршруты'), state=FindJourneysStates.choosing_orders, id="orders"),
        Button(text=Const("Назад"), on_click=back_to_menu, id="courier_menu")
    ),
    state=FindJourneysStates.filtering
)
choosing_source_city = Window(
    Const('Выбери город отправления'),
    ScrollingGroup(
        Select(
            Format("{item}"),
            id="source_city_select",  # Поменяли ID
            items='source_cities',
            item_id_getter=lambda x: x,  # Получаем ID как строку
            on_click=on_source_city_selected,
        ),
        width=1,
        height=5,
        id="choosing_source_city"
    ),
    SwitchTo(text=Const('Назад'), state=FindJourneysStates.filtering, id="back_to_filtering"),
    getter=source_cities_getter,
    state=FindJourneysStates.choosing_source_city
)
choosing_destination_city = Window(
    Const('Выбери город назначения'),
    ScrollingGroup(
        Select(
            Format("{item}"),
            id="destination_city_select",  # Поменяли ID
            items='destination_cities',
            item_id_getter=lambda x: x,  # Получаем ID как строку
            on_click=on_destination_city_selected,
        ),
        width=1,
        height=5,
        id="choosing_destination_city"
    ),
    SwitchTo(text=Const('Назад'), state=FindJourneysStates.filtering, id="back_to_filtering"),
    getter=destination_cities_getter,
    state=FindJourneysStates.choosing_destination_city
)
orders_choose = Window(
    Const('Выбери интересующий заказ из списка'),
    ScrollingGroup(
        Select(
            Format("{item.delivery_city}"),
            id="request_select",  # Поменяли ID
            items='requests',
            item_id_getter=lambda x: x.courier_request_id,  # Получаем ID как строку
            on_click=on_orders_selected,
        ),
        width=1,
        height=5,
        id="choosing_request"
    ),
    SwitchTo(Const('Назад'), state=FindJourneysStates.filtering, id='back_to_filtering'),
    getter=orders_getter,
    state=FindJourneysStates.choosing_orders
)
order_choosed = Window(
    Format("<b>Адрес отправки</b>: {dialog_data[request].shipping_country}, {dialog_data[request].shipping_state}, {dialog_data[request].shipping_city}\n"
            "<b>Адрес доставки</b>: {dialog_data[request].delivery_country}, {dialog_data[request].delivery_state}, {dialog_data[request].delivery_city}\n"
            "<b>Комментарий</b>: {dialog_data[request].comment}"),
    Column(SwitchTo(Const('Создать заявку'),'weight', FindJourneysStates.weight),
        SwitchTo(Const('Назад'),'back_to_choosing_orders', FindJourneysStates.choosing_orders)),
    state=FindJourneysStates.enrolling,
    parse_mode="HTML"
)
weight_window = Window(
    Const("Введите вес посылки (кг):"),
    MessageInput(on_weight_changed),
    Button(Const("Волшебная кнопка"), on_click=magic_button, id="magic_button"),
    Back(Const("Назад"), show_mode=ShowMode.EDIT),
    state=FindJourneysStates.weight,
)
length_window = Window(
    Const("Введите размер посылки в длину (см):"),
    MessageInput(on_length_changed),
    Back(Const("Назад"), show_mode=ShowMode.EDIT),
    state=FindJourneysStates.length,
)
width_window = Window(
    Const("Введите размер посылки в ширину (см):"),
    MessageInput(on_width_changed),
    Back(Const("Назад")),
    state=FindJourneysStates.width,
)
height_window = Window(
    Const("Введите размер посылки в высоту (см):"),
    MessageInput(on_height_changed),
    Back(Const("Назад"), show_mode=ShowMode.EDIT),
    state=FindJourneysStates.height,
)
cost_window = Window(
    Const("Введите цену доставки (руб):"),
    MessageInput(on_cost_changed),
    Back(Const("Назад"), show_mode=ShowMode.EDIT),
    state=FindJourneysStates.cost,
)
shipping_street_window = Window(
    Format("<b>Данные по месту отправки, которые уже введены</b>: {dialog_data[shipping_country]}, {dialog_data[shipping_state]}, {dialog_data[shipping_city]}\n"
           "Дополните их\nВведите улицу:"),
    MessageInput(on_shipping_street_changed),
    Back(Const("Назад"), show_mode=ShowMode.EDIT),
    state=FindJourneysStates.shipping_street,
    parse_mode="HTML"
)
shipping_house_window = Window(
    Format("<b>Данные по месту отправки, которые уже введены</b>: {dialog_data[shipping_country]}, {dialog_data[shipping_state]}, {dialog_data[shipping_city]}\n"
           "Дополните их\nВведите дом:"),
    MessageInput(on_shipping_house_changed),
    Back(Const("Назад"), show_mode=ShowMode.EDIT),
    state=FindJourneysStates.shipping_house,
    parse_mode="HTML"
)
shipping_postal_code_window = Window(
    Format("<b>Данные по месту отправки, которые уже введены</b>: {dialog_data[shipping_country]}, {dialog_data[shipping_state]}, {dialog_data[shipping_city]}\n"
           "Дополните их\nВведите почтовый индекс:"),
    MessageInput(on_shipping_postal_code_changed),
    Back(Const("Назад"), show_mode=ShowMode.EDIT),
    state=FindJourneysStates.shipping_postal_code,
    parse_mode="HTML"
)
delivery_street_window = Window(
    Format("<b>Данные по месту доставки, которые уже введены</b>: {dialog_data[delivery_country]}, {dialog_data[delivery_state]}, {dialog_data[delivery_city]}\n"
           "Дополните их\nВведите улицу:"),
    MessageInput(on_delivery_street_changed),
    Back(Const("Назад"), show_mode=ShowMode.EDIT),
    state=FindJourneysStates.delivery_street,
    parse_mode="HTML"
)
delivery_house_window = Window(
    Format("<b>Данные по месту доставки, которые уже введены</b>: {dialog_data[delivery_country]}, {dialog_data[delivery_state]}, {dialog_data[delivery_city]}\n"
           "Дополните их\nВведите дом:"),
    MessageInput(on_delivery_house_changed),
    Back(Const("Назад"), show_mode=ShowMode.EDIT),
    state=FindJourneysStates.delivery_house,
    parse_mode="HTML"
)
delivery_postal_code_window = Window(
    Format("<b>Данные по месту доставки, которые уже введены</b>: {dialog_data[delivery_country]}, {dialog_data[delivery_state]}, {dialog_data[delivery_city]}\n"
           "Дополните их\nВведите почтовый индекс:"),
    MessageInput(on_delivery_postal_code_changed),
    Back(Const("Назад"), show_mode=ShowMode.EDIT),
    state=FindJourneysStates.delivery_postal_code,
    parse_mode="HTML"
)
rec_name_window = Window(
    Const("Введите имя получателя:"),
    MessageInput(on_rec_name_changed),
    Back(Const("Назад"), show_mode=ShowMode.EDIT),
    state=FindJourneysStates.rec_name,
)
rec_email_window = Window(
    Const("Чтобы курьер смог связаться с получателем при возникновении проблемы, настоятельно рекомендуется заполнить хотя бы одно поле из следующих трёх: почта, телефон, телеграм.\nВведите почту получателя в формате your_mail_name@domain.ru:"),
    MessageInput(
        on_rec_email_changed, filter=~F.text.lower().in_(["пропустить"])
    ),
    Row(
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        Button(Const("Пропустить"), "skip", on_click=on_skip_rec_email),
    ),
    state=FindJourneysStates.rec_email,
)
rec_phone_window = Window(
    Const("Введите номер телефона получателя в формате +79999999999:"),
    MessageInput(
        on_rec_phone_changed, filter=~F.text.lower().in_(["пропустить"])
    ),
    Row(
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        Button(Const("Пропустить"), "skip", on_click=on_skip_rec_phone),
    ),
    state=FindJourneysStates.rec_phone,
)
rec_telegram_window = Window(
    Const("Введите телеграм получателя:"),
    MessageInput(on_rec_telegram_id_changed),
    Row(
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        Button(Const("Пропустить"), "skip", on_click=on_skip_rec_telegram_id),
    ),
    state=FindJourneysStates.rec_telegram_id,
)
check_process_window = Window(
    Format(
        "Все данные заполнены!\n"
        "Пожалуйста, проверьте все ли верно:\n"
        "<b>Вес посылки</b>: {weight} кг\n"
        "<b>Длина посылки</b>: {length} см\n"
        "<b>Ширина посылки</b>: {width} см\n"
        "<b>Высота посылки</b>: {height} см\n"
        "<b>Цена доставки</b>: {cost} руб\n"
        "<b>Адрес отправки</b>: {shipping_country}, {shipping_state}, {shipping_city}, {shipping_street}, {shipping_house}, {shipping_postal_code}\n"
        "<b>Адрес доставки</b>: {delivery_country}, {delivery_state}, {delivery_city}, {delivery_street}, {delivery_house}, {delivery_postal_code}\n"
        "<b>Имя получателя</b>: {rec_name}\n"
        "<b>Почта получателя</b>: {rec_email}\n"
        "<b>Телефон получателя</b>: {rec_phone}\n"
        "<b>Телеграм получателя</b>: {rec_telegram_id}\n"
        "<b>ВАЖНО</b>:Нажимая кнопку 'Всё верно', вы даёте согласие на передачу персональных данных потенциальным доставщикам"
    ),
    Button(Const("Все верно"), id="finish", on_click=on_finish_clicked),
    Button(Const("Неверно, начать сначала"), id="restart", on_click=on_restart_clicked),
    Back(Const('Назад'), show_mode=ShowMode.EDIT),
    parse_mode="HTML",
    state=FindJourneysStates.check_process,
    getter=get_safe_form_data,
)

orders_choose_dialog = Dialog(orders_choose, order_choosed, filtering, choosing_destination_city, choosing_source_city, weight_window, length_window, width_window, height_window, cost_window, shipping_street_window, shipping_house_window, shipping_postal_code_window, delivery_street_window, delivery_house_window, delivery_postal_code_window, rec_name_window, rec_email_window, rec_phone_window, rec_telegram_window, check_process_window,
                              on_start=on_dialog_start)
dialog_router.include_router(orders_choose_dialog)


@dialog_router.callback_query(F.data == "find_journey") 
async def start_choosing(call: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(FindJourneysStates.filtering, mode=StartMode.RESET_STACK)
