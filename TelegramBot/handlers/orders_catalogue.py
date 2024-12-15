import asyncio
import logging
from typing import Any

from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button
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
from TelegramBot.data_base import get_db, User, Package
from sqlalchemy.orm import Session
from TelegramBot.keyboards import keyboards
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog
from TelegramBot.handlers.main_handler import MainForms
class orders_catalogue(StatesGroup):
    choosing_orders = State()
    enrolling = State()
router = Router()
async def orders_getter(dialog_manager: DialogManager, **_kwargs):
    db: Session = next(get_db())
    packages = db.query(Package).all()
    print(packages)
    packages = [{'package_id': 1, 'delivery_city': 'Moscow'}]
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
            Format("{item[delivery_city]}"),
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
    # Записали в БД
    #
    await c.answer('Отправили отклик покупателю!')
orders_editing = Window(
    Format('Вы выбрали посылку:{dialog_data[package_id]}'),
    Button(
        Const('Откликнуться'),
        on_click=add_enroll,
        id='enroll_button'
    ),
    state=orders_catalogue.enrolling
)
orders_choose_dialog = Dialog(orders_choose, orders_editing)
router.include_router(orders_choose_dialog)
setup_dialogs(router)
@router.callback_query(F.data=="orders_catalogue", MainForms.choosing)
async def start_questionnaire_process(call: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.start(orders_catalogue.choosing_orders, mode=StartMode.RESET_STACK)