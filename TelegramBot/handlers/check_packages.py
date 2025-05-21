import datetime
import re

import aiogram_dialog.api.entities.modes
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import DialogManager, Window, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Column, SwitchTo, Back
from aiogram_dialog.widgets.text import Const, Format
from typing import Any
from TelegramBot.handlers.payment import send_payment_invoice
from aiogram_dialog import (
    Data,
    Dialog,
    DialogManager,
    ShowMode,
    StartMode,
    Window,
)

from aiogram.types import InlineKeyboardButton
from asyncio import sleep

from TelegramBot.data_base import get_db, Package, User, PackageNote, Courier
from sqlalchemy.orm import Session
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram_dialog import Dialog
from TelegramBot.keyboards import keyboards
from TelegramBot.logging_helper import set_info_log
from TelegramBot.create_bot import bot
from TelegramBot.enum_types import *

# ==== Создаем отдельный роутер для диалогов ====
dialog_router = Router()


class CatalogueOwnPackages(StatesGroup):
    choosing_orders = State()
    view = State()
    changing = State()
    edit_weight = State()
    edit_length = State()
    edit_width = State()
    edit_height = State()
    edit_cost = State()
    edit_shipping = State()
    edit_delivery = State()
    edit_recipient_name = State()
    edit_recipient_email = State()
    edit_recipient_phone = State()
    edit_recipient_telegram = State()


async def on_dialog_start(start_data: Any, manager: DialogManager):
    pass

async def orders_getter(dialog_manager: DialogManager, **kwargs):
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == dialog_manager.event.from_user.id).first()
    packages = db.query(Package).filter(Package.customer_id == user.user_id)
    return {
        'packages': packages
    }

async def on_orders_selected(callback: CallbackQuery, widget: Any, manager: DialogManager,
                             item: int):  # item теперь строка!
    manager.dialog_data['package_id'] = item  # item - это ID который мы получим
    db: Session = next(get_db())
    manager.dialog_data['package'] = db.query(Package).filter(Package.package_id == item).first()
    await manager.switch_to(CatalogueOwnPackages.view)

async def process_weight_input(message: Message, widget: Any, manager: DialogManager):
    try:
        new_weight = float(message.text)
    except ValueError:
        error_message = await message.answer("Пожалуйста, введите числовое значение для веса.")
        await sleep(3)
        try:
            await error_message.delete()
        except Exception as e:
            pass
        try:
            await message.delete()
        except Exception as e:
            pass
        await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)
        return
    db: Session = next(get_db())
    package = db.query(Package).filter(Package.package_id == manager.dialog_data.get('package').package_id).first()
    if package:
        package.weight = new_weight   
        db.commit()                   
        manager.dialog_data['package'] = package
    else:
        await message.answer("Не удалось найти посылку для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Вес посылки успешно изменён на {new_weight} кг.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)

async def process_length_input(message: Message, widget: Any, manager: DialogManager):
    try:
        new_length = float(message.text)
    except ValueError:
        error_message = await message.answer("Пожалуйста, введите числовое значение для длины.")
        await sleep(3)
        try:
            await error_message.delete()
        except Exception as e:
            pass
        try:
            await message.delete()
        except Exception as e:
            pass
        await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)
        return
    db: Session = next(get_db())
    package = db.query(Package).filter(Package.package_id == manager.dialog_data.get('package').package_id).first()
    if package:
        package.length = new_length   
        db.commit()                   
        manager.dialog_data['package'] = package
    else:
        await message.answer("Не удалось найти посылку для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Длина посылки успешно изменена на {new_length} см.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)

async def process_width_input(message: Message, widget: Any, manager: DialogManager):
    try:
        new_width = float(message.text)
    except ValueError:
        error_message = await message.answer("Пожалуйста, введите числовое значение для ширины.")
        await sleep(3)
        try:
            await error_message.delete()
        except Exception as e:
            pass
        try:
            await message.delete()
        except Exception as e:
            pass
        await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)
        return
    db: Session = next(get_db())
    package = db.query(Package).filter(Package.package_id == manager.dialog_data.get('package').package_id).first()
    if package:
        package.width = new_width  
        db.commit()                   
        manager.dialog_data['package'] = package
    else:
        await message.answer("Не удалось найти посылку для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Ширина посылки успешно изменена на {new_width} см.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)

async def process_height_input(message: Message, widget: Any, manager: DialogManager):
    try:
        new_height = float(message.text)
    except ValueError:
        error_message = await message.answer("Пожалуйста, введите числовое значение для высоты.")
        await sleep(3)
        try:
            await error_message.delete()
        except Exception as e:
            pass
        try:
            await message.delete()
        except Exception as e:
            pass
        await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)
        return
    db: Session = next(get_db())
    package = db.query(Package).filter(Package.package_id == manager.dialog_data.get('package').package_id).first()
    if package:
        package.height = new_height  
        db.commit()                   
        manager.dialog_data['package'] = package
    else:
        await message.answer("Не удалось найти посылку для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Высота посылки успешно изменена на {new_height} см.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)

async def process_cost_input(message: Message, widget: Any, manager: DialogManager):
    try:
        new_cost = float(message.text)
    except ValueError:
        error_message = await message.answer("Пожалуйста, введите числовое значение для цены.")
        await sleep(3)
        try:
            await error_message.delete()
        except Exception as e:
            pass
        try:
            await message.delete()
        except Exception as e:
            pass
        await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)
        return
    db: Session = next(get_db())
    package = db.query(Package).filter(Package.package_id == manager.dialog_data.get('package').package_id).first()
    if package:
        package.cost = new_cost  
        db.commit()                   
        manager.dialog_data['package'] = package
    else:
        await message.answer("Не удалось найти посылку для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Цена доставки успешно изменена на {new_cost} руб.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)

async def process_recipient_name_input(message: Message, widget: Any, manager: DialogManager):
    new_name = message.text
    new_name = new_name.lower().capitalize()
    db: Session = next(get_db())
    package = db.query(Package).filter(Package.package_id == manager.dialog_data.get('package').package_id).first()
    if package:
        package.recipient_name = new_name  
        db.commit()                   
        manager.dialog_data['package'] = package
    else:
        await message.answer("Не удалось найти посылку для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Имя получателя успешно изменено на {new_name}.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)

async def process_recipient_email_input(message: Message, widget: Any, manager: DialogManager):
    new_email = message.text
    if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", message.text):
        db: Session = next(get_db())
        package = db.query(Package).filter(Package.package_id == manager.dialog_data.get('package').package_id).first()
        if package:
            package.recipient_email = new_email  
            db.commit()                   
            manager.dialog_data['package'] = package
        else:
            await message.answer("Не удалось найти посылку для обновления.")
        try:
            await message.delete()
        except Exception as e:
            pass
        confirmation_message = await message.answer(f"Email получателя успешно изменен на {new_email}.")
        await sleep(5)
        try:
            await confirmation_message.delete()
        except Exception as e:
            pass
        await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)
    else:
        error_message = await message.answer("Пожалуйста, введите корректную почту.")
        await sleep(3)
        try:
            await error_message.delete()
        except Exception as e:
            pass
        try:
            await message.delete()
        except Exception as e:
            pass
        await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)
        return
    
async def process_recipient_phone_input(message: Message, widget: Any, manager: DialogManager):
    new_phone = message.text
    if len(new_phone) <= 17:
        db: Session = next(get_db())
        package = db.query(Package).filter(Package.package_id == manager.dialog_data.get('package').package_id).first()
        if package:
            package.recipient_phone = new_phone  
            db.commit()                   
            manager.dialog_data['package'] = package
        else:
            await message.answer("Не удалось найти посылку для обновления.")
        try:
            await message.delete()
        except Exception as e:
            pass
        confirmation_message = await message.answer(f"Телефон получателя успешно изменен на {new_phone}.")
        await sleep(5)
        try:
            await confirmation_message.delete()
        except Exception as e:
            pass
        await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)
    else:
        error_message = await message.answer("Пожалуйста, введите корректный телефон.")
        await sleep(3)
        try:
            await error_message.delete()
        except Exception as e:
            pass
        try:
            await message.delete()
        except Exception as e:
            pass
        await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)
        return
    
async def process_recipient_telegram_input(message: Message, widget: Any, manager: DialogManager):
    new_tg = message.text
    db: Session = next(get_db())
    package = db.query(Package).filter(Package.package_id == manager.dialog_data.get('package').package_id).first()
    if package:
        package.recipient_telegram_id = new_tg  
        db.commit()                   
        manager.dialog_data['package'] = package
    else:
        await message.answer("Не удалось найти посылку для обновления.")
    try:
        await message.delete()
    except Exception as e:
        pass
    confirmation_message = await message.answer(f"Телеграм получателя успешно изменен на {new_tg}.")
    await sleep(5)
    try:
        await confirmation_message.delete()
    except Exception as e:
        pass
    await manager.switch_to(CatalogueOwnPackages.view, show_mode=ShowMode.EDIT)

async def back_to_message(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.delete()
    await callback.message.answer(
        text="Меню заказчика:",
        reply_markup=keyboards.user_menu()
    )
    await manager.done()

async def payment(callback: CallbackQuery, button: Button, manager: DialogManager):
    # await callback.message.delete()
    await send_payment_invoice(bot, callback.message.chat.id, manager.dialog_data.get("package_id"))
    # await manager.done()

edit_dialog = Dialog(
    Window(
        Const('Выбери интересующий заказ из списка'),
        ScrollingGroup(
            Select(
                Format("{item.delivery_city}"),
                id="package_select",  # Поменяли ID
                items='packages',
                item_id_getter=lambda x: x.package_id,  # Получаем ID как строку
                on_click=on_orders_selected,
            ),
            width=1,
            height=5,
            id="choosing_package"
        ),
        Button(text=Const("Назад"), on_click=back_to_message, id="back_to_message"),
        getter=orders_getter,
        state=CatalogueOwnPackages.choosing_orders
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
            "<b>Телеграм получателя</b>: {dialog_data[package].recipient_telegram_id}\n"
            "<b>Статус посылки</b>: {dialog_data[package].package_status.value}\n"
            "<b>Текущая локация</b>: {dialog_data[package].current_location}\n"),
        Column(SwitchTo(Const('Изменить'), 'changing', CatalogueOwnPackages.changing),
            Button(text=Const("Оплатить"), on_click=payment, id="payment"),
            SwitchTo(Const('Назад'),'back_to_choosing_orders', CatalogueOwnPackages.choosing_orders)),
        state=CatalogueOwnPackages.view,
        parse_mode="HTML"
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
            "<b>Телеграм получателя</b>: {dialog_data[package].recipient_telegram_id}\n"
            "<b>Статус посылки</b>: {dialog_data[package].package_status.value}\n"
            "<b>Текущая локация</b>: {dialog_data[package].current_location}\n\n"
            "<b>Что вы хотите изменить?</b>"),  # Проверьте вывод в чат
        Column(
            SwitchTo(Const('Изменить вес'), id="edit_weight", state=CatalogueOwnPackages.edit_weight),
            SwitchTo(Const('Изменить длину'), id="edit_length", state=CatalogueOwnPackages.edit_length),
            SwitchTo(Const('Изменить ширину'), id="edit_width", state=CatalogueOwnPackages.edit_width),
            SwitchTo(Const('Изменить высоту'), id="edit_height", state=CatalogueOwnPackages.edit_height),
            SwitchTo(Const('Изменить цену доставки'), id="edit_cost", state=CatalogueOwnPackages.edit_cost),
            SwitchTo(Const('Изменить адрес отправки'), id="edit_shipping", state=CatalogueOwnPackages.edit_shipping),
            SwitchTo(Const('Изменить адрес доставки'), id="edit_delivery", state=CatalogueOwnPackages.edit_delivery),
            SwitchTo(Const('Изменить имя получателя'), id="edit_recipient_name", state=CatalogueOwnPackages.edit_recipient_name),
            SwitchTo(Const('Изменить почту получателя'), id="edit_recipient_email", state=CatalogueOwnPackages.edit_recipient_email),
            SwitchTo(Const('Изменить телефон получателя'), id="edit_recipient_phone", state=CatalogueOwnPackages.edit_recipient_phone),
            SwitchTo(Const('Изменить телеграм получателя'), id="edit_recipient_telegram", state=CatalogueOwnPackages.edit_recipient_telegram),
            SwitchTo(Const('Назад'),'back_to_choosing_orders', CatalogueOwnPackages.view)),
        state=CatalogueOwnPackages.changing,
        parse_mode="HTML"
    ),
    Window(
        Const("Введите новый вес посылки (в кг):"),
        MessageInput(process_weight_input),
        Back(text=Const("Назад"), on_click=lambda c, b, m: m.switch_to(CatalogueOwnPackages.changing)),
        state=CatalogueOwnPackages.edit_weight
    ),
    Window(
        Const("Введите новую длину посылки (в см):"),
        MessageInput(process_length_input),
        Back(text=Const("Назад"), on_click=lambda c, b, m: m.switch_to(CatalogueOwnPackages.changing)),
        state=CatalogueOwnPackages.edit_length
    ),
    Window(
        Const("Введите новую ширину посылки (в см):"),
        MessageInput(process_width_input),
        Back(text=Const("Назад"), on_click=lambda c, b, m: m.switch_to(CatalogueOwnPackages.changing)),
        state=CatalogueOwnPackages.edit_width
    ),
    Window(
        Const("Введите новую высоту посылки (в см):"),
        MessageInput(process_height_input),
        Back(text=Const("Назад"), on_click=lambda c, b, m: m.switch_to(CatalogueOwnPackages.changing)),
        state=CatalogueOwnPackages.edit_height
    ),
    Window(
        Const("Введите новую цену перевозки (в руб):"),
        MessageInput(process_cost_input),
        Back(text=Const("Назад"), on_click=lambda c, b, m: m.switch_to(CatalogueOwnPackages.changing)),
        state=CatalogueOwnPackages.edit_cost
    ),
    Window(
        Const("Введите новое имя получателя:"),
        MessageInput(process_recipient_name_input),
        Back(text=Const("Назад"), on_click=lambda c, b, m: m.switch_to(CatalogueOwnPackages.changing)),
        state=CatalogueOwnPackages.edit_recipient_name
    ),
    Window(
        Const("Введите новую почту получателя:"),
        MessageInput(process_recipient_email_input),
        Back(text=Const("Назад"), on_click=lambda c, b, m: m.switch_to(CatalogueOwnPackages.changing)),
        state=CatalogueOwnPackages.edit_recipient_email
    ),
    Window(
        Const("Введите новый телефон получателя:"),
        MessageInput(process_recipient_phone_input),
        Back(text=Const("Назад"), on_click=lambda c, b, m: m.switch_to(CatalogueOwnPackages.changing)),
        state=CatalogueOwnPackages.edit_recipient_phone
    ),
    Window(
        Const("Введите новый телеграм получателя:"),
        MessageInput(process_recipient_telegram_input),
        Back(text=Const("Назад"), on_click=lambda c, b, m: m.switch_to(CatalogueOwnPackages.changing)),
        state=CatalogueOwnPackages.edit_recipient_telegram
    )
)

# ==== Регистрируем диалог в роутере dialog_router ====
dialog_router.include_router(edit_dialog)


# ==== Хендлер для запуска диалога ====
@dialog_router.callback_query(F.data == "track")  # Исправленный фильтр
async def start_choosing(call: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(CatalogueOwnPackages.choosing_orders, mode=StartMode.RESET_STACK)
