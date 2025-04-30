import datetime

import aiogram_dialog.api.entities.modes
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import DialogManager, Window, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Column, Row, SwitchTo, Back
from aiogram_dialog.widgets.text import Const, Format
from typing import Any
from aiogram_dialog import (
    Data,
    Dialog,
    DialogManager,
    ShowMode,
    StartMode,
    Window,
)

from aiogram.types import InlineKeyboardButton
from asyncio import sleep, create_task

from TelegramBot.data_base import get_db, Package, User, PackageNote, Courier, Courier_Request
from sqlalchemy.orm import Session
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram_dialog import Dialog
from TelegramBot.keyboards import keyboards
from TelegramBot.logging_helper import set_info_log
from TelegramBot.create_bot import bot
from TelegramBot.enum_types import *

dialog_router = Router()

class CheckJourneysStates(StatesGroup):
    choosing_journey = State()
    view = State()
    delete_journey = State()
    changing = State()
    edit_shipping_country = State()
    edit_shipping_state = State()
    edit_shipping_city = State()
    edit_delivery_country = State()
    edit_delivery_state = State()
    edit_delivery_city = State()
    edit_comment = State()
    checking = State()
    enrolling = State()
    writing_note = State()

async def on_dialog_start(start_data: Any, manager: DialogManager):
    manager.dialog_data['enroll_comment'] = "Без комментария"

async def back_to_menu(callback: CallbackQuery, button: Button, manager: DialogManager):
    from TelegramBot.handlers.courier_menu import CourierMenuStates

    await callback.message.delete()
    await manager.start(CourierMenuStates.choosing_menu, mode=StartMode.RESET_STACK)

async def journeys_getter(dialog_manager: DialogManager, **kwargs):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == dialog_manager.event.from_user.id).first()
    courier: Courier = user.courier
    if courier is None:
        courier: Courier = Courier(user=user)
        db.add(courier)
        db.commit()
    journeys = db.query(Courier_Request).filter(Courier_Request.courier_id == courier.courier_id)
    return {
        'journeys': journeys
    }

async def on_journey_selected(callback: CallbackQuery, widget: Any, manager: DialogManager,
                             item: int):
    manager.dialog_data['journey_id'] = item
    db: Session = next(get_db())
    manager.dialog_data['journey'] = db.query(Courier_Request).filter(Courier_Request.courier_request_id == item).first()
    await manager.switch_to(CheckJourneysStates.view)

async def delete_journey(callback: CallbackQuery, widget: Any, manager: DialogManager):
    db: Session = next(get_db())
    req: Courier_Request | None = db.get(Courier_Request, manager.dialog_data['journey_id'])
    if req:
        db.delete(req)
        db.commit()
        message = await callback.bot.send_message(callback.message.chat.id, "Поездка удалена! 🗑️")
        create_task(delete_message_after_time(message))
    else:
        message = await callback.bot.send_message(callback.message.chat.id, "Не удалось найти запись(")
        create_task(delete_message_after_time(message))
    await manager.switch_to(CheckJourneysStates.choosing_journey)

async def delete_message_after_time(message: Message):
    await sleep(5)
    try:
        await message.delete()
    except Exception:
        pass

async def process_shipping_country(message: Message, widget: Any, manager: DialogManager):
    new_shipping_country = message.text
    db: Session = next(get_db())
    journey = db.query(Courier_Request).filter(Courier_Request.courier_request_id == manager.dialog_data.get('journey').courier_request_id).first()
    if journey:
        journey.shipping_country = new_shipping_country
        db.commit()                   
        manager.dialog_data['journey'] = journey
    else:
        await message.answer("Не удалось найти заявки для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Страна начала пути успешно изменена на {new_shipping_country}.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CheckJourneysStates.view, show_mode=ShowMode.EDIT)

async def process_shipping_state(message: Message, widget: Any, manager: DialogManager):
    new_shipping_state = message.text
    db: Session = next(get_db())
    journey = db.query(Courier_Request).filter(Courier_Request.courier_request_id == manager.dialog_data.get('journey').courier_request_id).first()
    if journey:
        journey.shipping_state = new_shipping_state
        db.commit()                   
        manager.dialog_data['journey'] = journey
    else:
        await message.answer("Не удалось найти заявки для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Штат/область/округ(и т.д.) начала пути успешно изменен на {new_shipping_state}.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CheckJourneysStates.view, show_mode=ShowMode.EDIT)

async def process_shipping_city(message: Message, widget: Any, manager: DialogManager):
    new_shipping_city = message.text
    db: Session = next(get_db())
    journey = db.query(Courier_Request).filter(Courier_Request.courier_request_id == manager.dialog_data.get('journey').courier_request_id).first()
    if journey:
        journey.shipping_city = new_shipping_city
        db.commit()                   
        manager.dialog_data['journey'] = journey
    else:
        await message.answer("Не удалось найти заявки для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Город начала пути успешно изменен на {new_shipping_city}.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CheckJourneysStates.view, show_mode=ShowMode.EDIT)

async def process_delivery_country(message: Message, widget: Any, manager: DialogManager):
    new_delivery_country = message.text
    db: Session = next(get_db())
    journey = db.query(Courier_Request).filter(Courier_Request.courier_request_id == manager.dialog_data.get('journey').courier_request_id).first()
    if journey:
        journey.delivery_country = new_delivery_country
        db.commit()                   
        manager.dialog_data['journey'] = journey
    else:
        await message.answer("Не удалось найти заявки для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Страна конца пути успешно изменена на {new_delivery_country}.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CheckJourneysStates.view, show_mode=ShowMode.EDIT)

async def process_delivery_state(message: Message, widget: Any, manager: DialogManager):
    new_delivery_state = message.text
    db: Session = next(get_db())
    journey = db.query(Courier_Request).filter(Courier_Request.courier_request_id == manager.dialog_data.get('journey').courier_request_id).first()
    if journey:
        journey.delivery_state = new_delivery_state
        db.commit()                   
        manager.dialog_data['journey'] = journey
    else:
        await message.answer("Не удалось найти заявки для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Штат/область/округ(и т.д.) конца пути успешно изменен на {new_delivery_state}.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CheckJourneysStates.view, show_mode=ShowMode.EDIT)

async def process_delivery_city(message: Message, widget: Any, manager: DialogManager):
    new_delivery_city = message.text
    db: Session = next(get_db())
    journey = db.query(Courier_Request).filter(Courier_Request.courier_request_id == manager.dialog_data.get('journey').courier_request_id).first()
    if journey:
        journey.delivery_city = new_delivery_city
        db.commit()                   
        manager.dialog_data['journey'] = journey
    else:
        await message.answer("Не удалось найти заявки для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Город конца пути успешно изменен на {new_delivery_city}.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CheckJourneysStates.view, show_mode=ShowMode.EDIT)

async def process_comment(message: Message, widget: Any, manager: DialogManager):
    new_comment = message.text
    db: Session = next(get_db())
    journey = db.query(Courier_Request).filter(Courier_Request.courier_request_id == manager.dialog_data.get('journey').courier_request_id).first()
    if journey:
        journey.comment = new_comment
        db.commit()                   
        manager.dialog_data['journey'] = journey
    else:
        await message.answer("Не удалось найти заявки для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Комментарий успешно изменен.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CheckJourneysStates.view, show_mode=ShowMode.EDIT)

async def orders_getter(dialog_manager: DialogManager, **kwargs):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == dialog_manager.event.from_user.id).first()
    courier = db.query(Courier).filter(Courier.user_id == user.user_id).first()
    journey_id = dialog_manager.dialog_data["journey"].courier_request_id
    # packages = db.query(Package).filter(Package.customer_id != user.user_id)
    packages = db.query(Package).filter(Package.courier_id == None, Package.courier_request_id == journey_id)
    return {
        'packages': packages
    }

async def on_orders_selected(callback: CallbackQuery, widget: Any, manager: DialogManager,
                             item: int):  # item теперь строка!
    manager.dialog_data['package_id'] = item  # item - это ID который мы получим
    db: Session = next(get_db())
    manager.dialog_data['package'] = db.query(Package).filter(Package.package_id == item, Package.courier_id == None).first()
    await manager.switch_to(CheckJourneysStates.enrolling)

    user_id = manager.event.from_user.id
    user = db.query(User).filter(User.telegram_id == user_id).first()
    set_info_log(db, user.telegram_id, user.user_id,
                 f"Пользователь стал доставщиком посылки {manager.dialog_data['package']}")
    
async def on_enroll_comment_changed(
        message: Message, dialog: MessageInput, manager: DialogManager
):
    manager.dialog_data['enroll_comment'] = message.text
    await message.delete()
    manager.show_mode = aiogram_dialog.api.entities.modes.ShowMode.EDIT

async def add_enroll(c: CallbackQuery, button: Button, manager: DialogManager):
    package: Package = manager.dialog_data.get('package')
    comment = manager.dialog_data.get('enroll_comment')
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == c.from_user.id).first()
    package_enroll: PackageNote = PackageNote(content=comment, sender=user, sender_type=SenderEnum.courier,
                                              package=package, creation_date=datetime.datetime.now())
    db.add(package_enroll)
    db.commit()
    kb_list = [
        [InlineKeyboardButton(text='Принять', callback_data=f"accept_enroll_{package.package_id}_{user.user_id}")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await bot.send_message(package.user.telegram_id,
                           f"Новый отклик на посылку #{package.package_id}\nПользователь:@{c.from_user.username}\nКомментарий:{comment}", reply_markup=keyboard)
    await c.answer("Отправили отклик покупателю!")
    await c.message.delete()
    await manager.done()
    await c.message.answer(text="Меню заказчика:", reply_markup=keyboards.user_menu())

dialog = Dialog(
    Window(
        Const('Выбери интересующую заявку из списка'),
        ScrollingGroup(
            Select(
                Format("{item.delivery_city}"),
                id="journey_select",
                items='journeys',
                item_id_getter=lambda x: x.courier_request_id,
                on_click=on_journey_selected,
            ),
            width=1,
            height=5,
            id="choosing_journey"
        ),
        Button(text=Const("Назад"), on_click=back_to_menu, id="back_to_menu"),
        getter=journeys_getter,
        state=CheckJourneysStates.choosing_journey
    ),
    Window(
        Format("<b>Адрес отправки</b>: {dialog_data[journey].shipping_country}, {dialog_data[journey].shipping_state}, {dialog_data[journey].shipping_city}\n"
            "<b>Адрес доставки</b>: {dialog_data[journey].delivery_country}, {dialog_data[journey].delivery_state}, {dialog_data[journey].delivery_city}\n"
            "<b>Комментарий</b>: {dialog_data[journey].comment}"),
        Column(SwitchTo(Const('Посмотреть заказы на данный маршрут'), 'check', CheckJourneysStates.checking),
            SwitchTo(Const('Изменить'), 'changing', CheckJourneysStates.changing),
            SwitchTo(Const('Удалить'), id="delete_journey", state=CheckJourneysStates.delete_journey),
            SwitchTo(Const('Назад'),'back_to_choosing_orders', CheckJourneysStates.choosing_journey)),
        state=CheckJourneysStates.view,
        parse_mode="HTML"
    ),
    Window(
        Const('Выбери интересующий заказ из списка'),
        ScrollingGroup(
            Select(
                Format("{item.delivery_city}"),
                id="package_select",
                items='packages',
                item_id_getter=lambda x: x.package_id,
                on_click=on_orders_selected,
            ),
            width=1,
            height=5,
            id="choosing_package"
            ),
        SwitchTo(Const('Назад'), state=CheckJourneysStates.view, id='back_to_filtering'),
        getter=orders_getter,
        state=CheckJourneysStates.checking
    ),
    Window(
        Format("<b>Вес посылки</b>: {dialog_data[package].weight} кг\n"
            "<b>Длина посылки</b>: {dialog_data[package].length} см\n"
            "<b>Ширина посылки</b>: {dialog_data[package].width} см\n"
            "<b>Высота посылки</b>: {dialog_data[package].height} см\n"
            "<b>Цена доставки</b>: {dialog_data[package].cost} руб\n"
            "<b>Адрес отправки</b>: {dialog_data[package].shipping_country}, {dialog_data[package].shipping_state}, {dialog_data[package].shipping_city}, {dialog_data[package].shipping_street}, {dialog_data[package].shipping_house}, {dialog_data[package].shipping_postal_code}\n"
            "<b>Адрес доставки</b>: {dialog_data[package].delivery_country}, {dialog_data[package].delivery_state}, {dialog_data[package].delivery_city}, {dialog_data[package].delivery_street}, {dialog_data[package].delivery_house}, {dialog_data[package].delivery_postal_code}\n"
            "<b>Имя получателя</b>: {dialog_data[package].recipient_name}\n"
            "<b>Почта получателя</b>: {dialog_data[package].recipient_email}\n"
            "<b>Телефон получателя</b>: {dialog_data[package].recipient_phone}\n"
            "<b>Телеграм получателя</b>: {dialog_data[package].recipient_telegram_id}\n"),  # Проверьте вывод в чат
        Column(SwitchTo(Const('Откликнуться'), 'switching_to_note_writing', CheckJourneysStates.writing_note),
            SwitchTo(Const('Назад'),'back_to_choosing_orders', CheckJourneysStates.checking)),
        state=CheckJourneysStates.enrolling,
        parse_mode="HTML"
    ),
    Window(
        Format(
            'Оставьте примечание покупателю(необязательно)\nПримечание:{dialog_data[enroll_comment]}\nВАЖНО:Нажимая кнопку "Отправить", вы даёте согласие на передачу ваших контактов покупателю для дальнейшей связи'),
        MessageInput(on_enroll_comment_changed),
        Column(Button(Const('Отправить'),
                    on_click=add_enroll,
                    id='courier_menu'),
            SwitchTo(Const('Назад'), 'back_to_order', CheckJourneysStates.enrolling)),
        state=CheckJourneysStates.writing_note
    ),
    Window(
        Format("<b>Вы уверены, что хотите удалить данную заяку?</b>"),
        Row(Button(text=Const("Да"), on_click=delete_journey, id="delete_journey"),
            SwitchTo(Const('Нет'), id="back", state=CheckJourneysStates.view)),
        state=CheckJourneysStates.delete_journey,
        parse_mode="HTML"
    ),
    Window(
        Format("<b>Адрес отправки</b>: {dialog_data[journey].shipping_country}, {dialog_data[journey].shipping_state}, {dialog_data[journey].shipping_city}\n"
            "<b>Адрес доставки</b>: {dialog_data[journey].delivery_country}, {dialog_data[journey].delivery_state}, {dialog_data[journey].delivery_city}\n"
            "<b>Комментарий</b>: {dialog_data[journey].comment}\n\n"
            "<b>Что вы хотите изменить?</b>"),
        Column(
            SwitchTo(Const('Изменить страну начала пути'), id="edit_shipping_country", state=CheckJourneysStates.edit_shipping_country),
            SwitchTo(Const('Изменить штат/область/округ(и т.д.) начала пути'), id="edit_shipping_state", state=CheckJourneysStates.edit_shipping_state),
            SwitchTo(Const('Изменить город начала пути'), id="edit_shipping_city", state=CheckJourneysStates.edit_shipping_city),
            SwitchTo(Const('Изменить страну конца пути'), id="edit_delivery_country", state=CheckJourneysStates.edit_delivery_country),
            SwitchTo(Const('Изменить штат/область/округ(и т.д.) конца пути'), id="edit_delivery_state", state=CheckJourneysStates.edit_delivery_state),
            SwitchTo(Const('Изменить город конца пути'), id="edit_delivery_city", state=CheckJourneysStates.edit_delivery_city),
            SwitchTo(Const('Изменить комментарий'), id="edit_comment", state=CheckJourneysStates.edit_comment),
            SwitchTo(Const('Назад'), id='back_view', state=CheckJourneysStates.view)),
        state=CheckJourneysStates.changing,
        parse_mode="HTML"
    ),
    Window(
        Const("Введите новую страну начала пути:"),
        MessageInput(process_shipping_country),
        SwitchTo(Const('Назад'), id='back_changing', state=CheckJourneysStates.changing),
        state=CheckJourneysStates.edit_shipping_country
    ),
    Window(
        Const("Введите новый(ую) штат/область/округ(и т.д.) начала пути:"),
        MessageInput(process_shipping_state),
        SwitchTo(Const('Назад'), id='back_changing', state=CheckJourneysStates.changing),
        state=CheckJourneysStates.edit_shipping_state
    ),
    Window(
        Const("Введите новый город начала пути:"),
        MessageInput(process_shipping_city),
        SwitchTo(Const('Назад'), id='back_changing', state=CheckJourneysStates.changing),
        state=CheckJourneysStates.edit_shipping_city
    ),
    Window(
        Const("Введите новую страну конца пути:"),
        MessageInput(process_delivery_country),
        SwitchTo(Const('Назад'), id='back_changing', state=CheckJourneysStates.changing),
        state=CheckJourneysStates.edit_delivery_country
    ),
    Window(
        Const("Введите новый(ую) штат/область/округ(и т.д.) конца пути:"),
        MessageInput(process_delivery_state),
        SwitchTo(Const('Назад'), id='back_changing', state=CheckJourneysStates.changing),
        state=CheckJourneysStates.edit_delivery_state
    ),
    Window(
        Const("Введите новый город конца пути:"),
        MessageInput(process_delivery_city),
        SwitchTo(Const('Назад'), id='back_changing', state=CheckJourneysStates.changing),
        state=CheckJourneysStates.edit_delivery_city
    ),
    Window(
        Const("Введите новый комментарий:"),
        MessageInput(process_comment),
        SwitchTo(Const('Назад'), id='back_changing', state=CheckJourneysStates.changing),
        state=CheckJourneysStates.edit_comment
    ),
    on_start=on_dialog_start
)

dialog_router.include_router(dialog)

@dialog_router.callback_query(F.data == "check_journeys")
async def start_choosing(call: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(CheckJourneysStates.choosing_journey, mode=StartMode.RESET_STACK)