from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import DialogManager, Window, StartMode
from aiogram_dialog.widgets.kbd import Button, Column
from aiogram_dialog.widgets.text import Const
from typing import Any
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog
from TelegramBot.keyboards import keyboards
from TelegramBot.enum_types import *
from TelegramBot.handlers.new_create_request import Form
from TelegramBot.handlers.new_catalogue import Catalogue
from TelegramBot.handlers.package_choice import ChangePackageStatus
from TelegramBot.handlers.create_journey import CreateJourneyForm
from TelegramBot.handlers.check_journeys import CheckJourneysStates
from aiogram_dialog.api.entities.modes import ShowMode

dialog_router = Router()

class CourierMenuStates(StatesGroup):
    choosing_menu = State()

async def on_dialog_start(start_data: Any, manager: DialogManager):
    pass

async def create_journey(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.delete()
    await manager.start(
        CreateJourneyForm.shipping_country, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT
    )

async def check_journeys(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.delete()
    await manager.start(
        CheckJourneysStates.choosing_journey, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT
    )

async def new_catalogue(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.delete()
    await manager.start(Catalogue.filtering, mode=StartMode.RESET_STACK)

async def package_choice(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.delete()
    await manager.start(ChangePackageStatus.package_selection, mode=StartMode.RESET_STACK,
                               show_mode=ShowMode.EDIT)

async def back_to_message(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.delete()
    await callback.message.answer(
        text="Меню заказчика:",
        reply_markup=keyboards.user_menu()
    )
    await manager.done()

courier_menu = Window(
    Const('Меню доставщика:'),
    Column(
        Button(text=Const("Создать заявку на доставку"), on_click=create_journey, id="create_journey"),
        Button(text=Const("Посмотреть свои заявки"), on_click=check_journeys, id="check_journeys"),
        Button(text=Const("Каталог посылок"), on_click=new_catalogue, id="orders_catalogue"),
        Button(text=Const("Доставляемые посылки"), on_click=package_choice, id="package_choice"),
        Button(text=Const("⬅️Перейти в меню заказчика⬅️"), on_click=back_to_message, id="back_to_message")),
    state=CourierMenuStates.choosing_menu
)

courier_menu_dialog = Dialog(courier_menu, on_start=on_dialog_start)

dialog_router.include_router(courier_menu_dialog)

@dialog_router.callback_query(F.data == "courier_menu")
async def start_choosing(call: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(CourierMenuStates.choosing_menu, mode=StartMode.RESET_STACK)
