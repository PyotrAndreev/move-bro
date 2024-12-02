import asyncio
import logging
from typing import Any

from aiogram.enums import ContentType
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Radio, SwitchTo, Column
from aiogram_dialog.widgets.text import Const, Format

from TelegramBot.config import config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.formatting import Bold, Text
from aiogram.fsm.state import StatesGroup, State
import re
from aiogram_dialog import DialogManager, Window, setup_dialogs, StartMode
from ..data_base import get_db
from ..data_base import User, Package
from sqlalchemy.orm import Session
from ..keyboards import keyboards
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog
from ..handlers.main_handler import MainForms
class orders_catalogue(StatesGroup):
    filtering_orders = State()
    choosing_source_city = State()
    choosing_destination_city = State()
    choosing_orders = State()
    enrolling = State()
router = Router()
async def helper_message_source(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.answer("Введите город отправления")
async def helper_message_destination(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.answer("Введите город назначения")
orders_filtering = Window(
    Format('Фильтры посылок'),
    Column(
        SwitchTo(
        text=Const('Город отправления'),
        id='source_city_filtering',
        state=orders_catalogue.choosing_source_city,
        ),
        SwitchTo(
            text=Const('Город прибытия'),
            id='target_city_filtering',
            state=orders_catalogue.choosing_destination_city,
        ),
        SwitchTo(
            text=Const('Открыть каталог'),
            id='open_catalogue',
            state=orders_catalogue.choosing_orders
        )
    ),
    state=orders_catalogue.filtering_orders
)
async def choosing_source_city(message: Message,message_input: MessageInput, manager: DialogManager):
    manager.dialog_data['source_city'] = message.text
    await manager.switch_to(orders_catalogue.filtering_orders)
async def choosing_destination_city(message: Message,message_input: MessageInput, manager: DialogManager):
    manager.dialog_data['destination_city'] = message.text
    await manager.switch_to(orders_catalogue.filtering_orders)
choosing_source_city_window = Window(
    Const('Введите город отправления'),
    MessageInput(
        choosing_source_city, content_types=[ContentType.TEXT]
    ),
    state=orders_catalogue.choosing_source_city
)
choosing_destination_city_window = Window(
    Const('Введите город назначения'),
    MessageInput(
        choosing_destination_city, content_types=[ContentType.TEXT]
    ),
    state=orders_catalogue.choosing_destination_city
)
async def orders_getter(dialog_manager: DialogManager, **_kwargs):
    db: Session = next(get_db())
    # Пока обходимся без фильтров, когда будет API, отфильтруем
    packages = db.query(Package).all()
    packages = [{"package_id": 1, "source_city": dialog_manager.dialog_data['source_city'], "destination_city":dialog_manager.dialog_data['destination_city']}]
    return {
        'orders': packages
    }
async def on_order_selected(callback: CallbackQuery, widget: Any,
                            manager: DialogManager, item: int):
    manager.dialog_data['package_id'] = item
    await manager.next()
orders_choose = Window(
    Const('Выбери интересующий заказ из списка'),
    ScrollingGroup(
        Select(
            Format("{item[source_city]}"),
            id='s_orders',
            items='orders',
            item_id_getter=lambda x:x['package_id'],
            on_click=on_order_selected,
        ),
        width=1,
        height=5,
        id='scroll_with_pager'
    ),
    getter=orders_getter,
    state=orders_catalogue.choosing_orders
)
async def add_enroll(c: CallbackQuery, button: Button, manager: DialogManager):
    # Вызвали API для добавления отклика
    await c.answer('Отправили отклик покупателю!')
    await manager.switch_to(orders_catalogue.filtering_orders)
orders_editing = Window(
    Format('Вы выбрали посылку:\nID: {dialog_data[package_id]}\nГород отправления:{dialog_data[source_city]}\nГород назначения:{dialog_data[destination_city]}'),
    Button(
        Const('Откликнуться'),
        on_click=add_enroll,
        id='enroll_button'
    ),
    state=orders_catalogue.enrolling
)
orders_choose_dialog = Dialog(orders_filtering, choosing_source_city_window, choosing_destination_city_window, orders_choose, orders_editing)
router.include_router(orders_choose_dialog)
setup_dialogs(router)
@router.message(F.text=="Каталог посылок", MainForms.choosing)
async def start_questionnaire_process(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.start(orders_catalogue.filtering_orders, mode=StartMode.RESET_STACK)
