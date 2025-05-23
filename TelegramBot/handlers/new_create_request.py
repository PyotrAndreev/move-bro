import re

from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import (
    Data,
    Dialog,
    DialogManager,
    ShowMode,
    StartMode,
    Window,
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Cancel,
    Row,
    Button, Back
)
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy.orm import Session
from asyncio import sleep, create_task

from TelegramBot.data_base import Package, User, get_db
from TelegramBot.keyboards import keyboards

from TelegramBot.logging_helper import set_info_log

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
        "comment": data.get("comment"),
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
        "comment": safe_val("comment"),
    }

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

async def on_shipping_country_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if 2 <= len(message.text) <= 40:
        manager.dialog_data["shipping_country"] = message.text
        await manager.next(show_mode=ShowMode.EDIT)
    else:
        await message.answer("Пожалуйста, введите от 2 до 40 символов")

async def on_shipping_state_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if 2 <= len(message.text) <= 40 or message.text.lower() == "пропустить":
        manager.dialog_data["shipping_state"] = (
            message.text if message.text.lower() != "пропустить" else None
        )
        await manager.next(show_mode=ShowMode.EDIT)
    else:
        await message.answer("Пожалуйста, введите от 2 до 40 символов")

async def on_shipping_city_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if 2 <= len(message.text) <= 40:
        manager.dialog_data["shipping_city"] = message.text
        await manager.next(show_mode=ShowMode.EDIT)
    else:
        await message.answer("Пожалуйста, введите от 2 до 40 символов")

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

async def on_delivery_country_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if 2 <= len(message.text) <= 40:
        manager.dialog_data["delivery_country"] = message.text
        await manager.next(show_mode=ShowMode.EDIT)
    else:
        await message.answer("Пожалуйста, введите от 2 до 40 символов")

async def on_delivery_state_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if 2 <= len(message.text) <= 40 or message.text.lower() == "пропустить":
        manager.dialog_data["delivery_state"] = (
            message.text if message.text.lower() != "пропустить" else None
        )
        await manager.next(show_mode=ShowMode.EDIT)
    else:
        await message.answer("Пожалуйста, введите от 2 до 40 символов")

async def on_delivery_city_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    if 2 <= len(message.text) <= 40:
        manager.dialog_data["delivery_city"] = message.text
        await manager.next(show_mode=ShowMode.EDIT)
    else:
        await message.answer("Пожалуйста, введите от 2 до 40 символов")

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
    await manager.switch_to(Form.check_process, show_mode=ShowMode.EDIT)

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
    await manager.switch_to(Form.check_process, show_mode=ShowMode.EDIT)
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
    manager.dialog_data['shipping_country'] = "RU"
    manager.dialog_data['shipping_state'] = None
    manager.dialog_data['shipping_city'] = "Moscow"
    manager.dialog_data['shipping_street'] = "Kremenchugskaya"
    manager.dialog_data['shipping_postal_code'] = 423333
    manager.dialog_data['shipping_house'] = 10
    manager.dialog_data['delivery_country'] = "US"
    manager.dialog_data['delivery_state'] = "Nebraska"
    manager.dialog_data['delivery_city'] = "Nebraska"
    manager.dialog_data['delivery_street'] = "Nebrosko"
    manager.dialog_data['delivery_house'] = 10
    manager.dialog_data['delivery_postal_code'] = 10101
    manager.dialog_data['rec_name'] = "FreddyBear"
    manager.dialog_data['rec_email'] = "freddy@scottgames.io"
    manager.dialog_data['rec_phone'] = "12345678910"
    manager.dialog_data['rec_telegram_id'] = "@freddy_pizzaman"
    await manager.switch_to(Form.check_process, show_mode=ShowMode.EDIT)







    await manager.switch_to(Form.check_process, show_mode=ShowMode.EDIT)
async def on_comment_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    manager.dialog_data["comment"] = message.text
    await manager.next(show_mode=ShowMode.EDIT)

async def on_restart_clicked(callback_query: CallbackQuery, button: Button, manager: DialogManager):
    await manager.done()
    await callback_query.message.delete()
    await manager.start(Form.weight, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT)

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
        user=user
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

async def go_back(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.delete()
    await manager.done()
    await callback.message.answer(text="Меню заказчика:", reply_markup=keyboards.user_menu())

dialog = Dialog(
    Window(
        Const("Введите вес посылки (кг):"),
        MessageInput(on_weight_changed),
        Button(Const("Назад"), on_click=go_back, id="go_back"),
        state=Form.weight,
    ),
    Window(
        Const("Введите размер посылки в длину (см):"),
        MessageInput(on_length_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.length,
    ),
    Window(
        Const("Введите размер посылки в ширину (см):"),
        MessageInput(on_width_changed),
        Back(Const("Назад")),
        state=Form.width,
    ),
    Window(
        Const("Введите размер посылки в высоту (см):"),
        MessageInput(on_height_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.height,
    ),
    Window(
        Const("Введите цену доставки (руб):"),
        MessageInput(on_cost_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.cost,
    ),
    Window(
        Const("Данные по месту отправки"),
        Const("Введите страну:"),
        MessageInput(on_shipping_country_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.shipping_country,
    ),
    Window(
        Const("Введите штат/область/округ(и т.д.):"),
        MessageInput(on_shipping_state_changed, filter=~F.text.lower().in_(["пропустить"])),
        Row(
            Back(Const("Назад"), show_mode=ShowMode.EDIT),
            Button(Const("Пропустить"), "skip", on_click=lambda c, b, m: m.next()),
        ),
        state=Form.shipping_state,
    ),
    Window(
        Const("Введите город:"),
        MessageInput(on_shipping_city_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.shipping_city,
    ),
    Window(
        Const("Введите улицу:"),
        MessageInput(on_shipping_street_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.shipping_street,
    ),
    Window(
        Const("Введите дом:"),
        MessageInput(on_shipping_house_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.shipping_house,
    ),
    Window(
        Const("Введите почтовый индекс:"),
        MessageInput(on_shipping_postal_code_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.shipping_postal_code,
    ),
    Window(
        Const("Данные по месту назначения"),
        Const("Введите страну:"),
        MessageInput(on_delivery_country_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.delivery_country,
    ),
    Window(
        Const("Введите штат/область/округ(и т.д.):"),
        MessageInput(on_delivery_state_changed, filter=~F.text.lower().in_(["пропустить"])),
        Row(
            Back(Const("Назад"), show_mode=ShowMode.EDIT),
            Button(Const("Пропустить"), "skip", on_click=lambda c, b, m: m.next()),
        ),
        state=Form.delivery_state,
    ),
    Window(
        Const("Введите город:"),
        MessageInput(on_delivery_city_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.delivery_city,
    ),
    Window(
        Const("Введите улицу:"),
        MessageInput(on_delivery_street_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.delivery_street,
    ),
    Window(
        Const("Введите дом:"),
        MessageInput(on_delivery_house_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.delivery_house,
    ),
    Window(
        Const("Введите почтовый индекс:"),
        MessageInput(on_delivery_postal_code_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.delivery_postal_code,
    ),
    Window(
        Const("Введите имя получателя:"),
        MessageInput(on_rec_name_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=Form.rec_name,
    ),
    Window(
        Const("Чтобы курьер смог связаться с получателем при возникновении проблемы, настоятельно рекомендуется заполнить хотя бы одно поле из следующих трёх: почта, телефон, телеграм.\nВведите почту получателя в формате your_mail_name@domain.ru:"),
        MessageInput(
            on_rec_email_changed, filter=~F.text.lower().in_(["пропустить"])
        ),
        Row(
            Back(Const("Назад"), show_mode=ShowMode.EDIT),
            Button(Const("Пропустить"), "skip", on_click=on_skip_rec_email),
        ),
        state=Form.rec_email,
    ),
    Window(
        Const("Введите номер телефона получателя в формате +79999999999:"),
        MessageInput(
            on_rec_phone_changed, filter=~F.text.lower().in_(["пропустить"])
        ),
        Row(
            Back(Const("Назад"), show_mode=ShowMode.EDIT),
            Button(Const("Пропустить"), "skip", on_click=on_skip_rec_phone),
        ),
        state=Form.rec_phone,
    ),
    Window(
        Const("Введите телеграм получателя:"),
        MessageInput(on_rec_telegram_id_changed),
        Row(
            Back(Const("Назад"), show_mode=ShowMode.EDIT),
            Button(Const("Пропустить"), "skip", on_click=on_skip_rec_telegram_id),
        ),
        state=Form.rec_telegram_id,
    ),
    Window(
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
        state=Form.check_process,
        getter=get_safe_form_data,
    ),
)

router.include_router(dialog)
@router.callback_query(F.data == "create_request")
async def start_request_process(
    callback_query: CallbackQuery, dialog_manager: DialogManager
):
    await dialog_manager.start(
        Form.weight, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT
    )