import datetime

import aiogram_dialog.api.entities.modes
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import DialogManager, Window, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Column, SwitchTo, Back
from aiogram_dialog.widgets.text import Const, Format
from typing import Any

from aiogram.types import InlineKeyboardButton

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


class Catalogue(StatesGroup):
    filtering = State()
    choosing_orders = State()
    enrolling = State()
    choosing_source_city = State()
    choosing_destination_city = State()
    writing_note = State()


async def on_dialog_start(start_data: Any, manager: DialogManager):
    manager.dialog_data['source_city'] = "Не выбран"
    manager.dialog_data['destination_city'] = "Не выбран"
    manager.dialog_data['enroll_comment'] = "Без комментария"


async def source_cities_getter(dialog_manager: DialogManager, **kwargs):
    db: Session = next(get_db())
    cities = db.query(Package.shipping_city.distinct())
    if dialog_manager.dialog_data.get('destination_city') != 'Не выбран':
        cities = cities.filter_by(delivery_city=dialog_manager.dialog_data.get('destination_city'))
    cities = cities.all()
    cities = [row[0] for row in cities]
    return {
        'source_cities': cities
    }


async def on_source_city_selected(callback: CallbackQuery, widget: Any, manager: DialogManager, item: str):
    manager.dialog_data['source_city'] = item
    await manager.switch_to(Catalogue.filtering)


async def destination_cities_getter(dialog_manager: DialogManager, **kwargs):
    db: Session = next(get_db())
    cities = db.query(Package.delivery_city.distinct())
    if dialog_manager.dialog_data.get('source_city') != 'Не выбран':
        cities = cities.filter_by(shipping_city=dialog_manager.dialog_data.get('source_city'))
    cities = cities.all()
    cities = [row[0] for row in cities]
    return {
        'destination_cities': cities
    }


async def on_destination_city_selected(callback: CallbackQuery, widget: Any, manager: DialogManager, item: str):
    manager.dialog_data['destination_city'] = item
    await manager.switch_to(Catalogue.filtering)


async def orders_getter(dialog_manager: DialogManager, **kwargs):
    db: Session = next(get_db())
    packages = db.query(Package)
    source_city = dialog_manager.dialog_data.get('source_city')
    destination_city = dialog_manager.dialog_data.get('destination_city')
    if source_city != 'Не выбран':
        packages = packages.filter_by(shipping_city=source_city)
    if destination_city != 'Не выбран':
        packages = packages.filter_by(delivery_city=destination_city)
    return {
        'packages': packages
    }


async def on_orders_selected(callback: CallbackQuery, widget: Any, manager: DialogManager,
                             item: int):  # item теперь строка!
    manager.dialog_data['package_id'] = item  # item - это ID который мы получим
    db: Session = next(get_db())
    manager.dialog_data['package'] = db.query(Package).filter(Package.package_id == item).first()
    await manager.switch_to(Catalogue.enrolling)

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
    courier: Courier = Courier(user=user)
    db.add(package_enroll)
    db.add(courier)
    db.commit()
    kb_list = [
        [InlineKeyboardButton(text='Принять', callback_data=f"accept_enroll_{package.package_id}_{user.user_id}")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await bot.send_message(package.user.telegram_id,
                           f"Новый отклик на посылку #{package.package_id}\nПользователь:@{c.from_user.username}\nКомментарий:{comment}", reply_markup=keyboard)
    await c.answer("Отправили отклик покупателю!")
    await c.message.answer(text="В данный момент вы находитесь в меню заказчика.", reply_markup=keyboards.user_menu())
    await manager.done()
async def back_to_menu(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.answer(text="В данный момент вы находитесь в меню заказчика.", reply_markup=keyboards.user_menu())
    await manager.done()

filtering = Window(
    Const('Настройте фильтры(при необходимости), после чего нажмите кнопку: "Заказы"'),
    Column(
        SwitchTo(text=Format("Город отправки: {dialog_data[source_city]}"), state=Catalogue.choosing_source_city,
                 id="source_city"),
        SwitchTo(text=Format("Город доставки: {dialog_data[destination_city]}"),
                 state=Catalogue.choosing_destination_city, id="destination_city"),
        SwitchTo(text=Const('Заказы'), state=Catalogue.choosing_orders, id="orders"),
        Button(text=Const("Назад"), on_click=back_to_menu, id="back_to_menu")
    ),
    state=Catalogue.filtering
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
    getter=source_cities_getter,
    state=Catalogue.choosing_source_city
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
    getter=destination_cities_getter,
    state=Catalogue.choosing_destination_city
)
orders_choose = Window(
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
    SwitchTo(Const('Назад'), state=Catalogue.filtering, id='back_to_filtering'),
    getter=orders_getter,
    state=Catalogue.choosing_orders
)
enrolling_note = Window(
    Format(
        'Оставьте примечание покупателю(необязательно)\nПримечание:{dialog_data[enroll_comment]}\nВАЖНО:Нажимая кнопку "Отправить", вы даёте согласие на передачу ваших контактов покупателю для дальнейшей связи'),
    MessageInput(on_enroll_comment_changed),
    Column(Button(Const('Отправить'),
                  on_click=add_enroll,
                  id='enroll'),
           SwitchTo(Const('Назад'), 'back_to_order', Catalogue.enrolling)),
    state=Catalogue.writing_note
)

order_choosed = Window(
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
    Column(SwitchTo(Const('Откликнуться'), 'switching_to_note_writing', Catalogue.writing_note),
        SwitchTo(Const('Назад'),'back_to_choosing_orders', Catalogue.choosing_orders)),
    state=Catalogue.enrolling,
    parse_mode="HTML"
)
orders_choose_dialog = Dialog(orders_choose, order_choosed, filtering, choosing_destination_city, choosing_source_city,enrolling_note,
                              on_start=on_dialog_start)
# ==== Регистрируем диалог в роутере dialog_router ====
dialog_router.include_router(orders_choose_dialog)


# ==== Хендлер для запуска диалога ====
@dialog_router.callback_query(F.data == "orders_catalogue")  # Исправленный фильтр
async def start_choosing(call: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(Catalogue.filtering, mode=StartMode.RESET_STACK)
