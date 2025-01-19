from operator import itemgetter
from typing import Any

from aiogram import F
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import Text
from aiogram_dialog import Dialog, StartMode
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.setup import setup_dialogs
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Radio, Button, Row, ScrollingGroup, Select, Back, Next, SwitchTo, Group
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy.orm import Session
from sqlalchemy.testing import only_if
from aiogram_dialog.api.entities.modes import ShowMode

from TelegramBot.data_base import User, Package, Courier, get_db
from TelegramBot.handlers.main_handler import MainForms
from TelegramBot.keyboards import keyboards
from TelegramBot.logging_helper import set_info_log, set_warn_log, set_error_log
from TelegramBot.enum_types import PackageStatusEnum

router = Router()


class ChangePackageStatus(StatesGroup):
    package_selection = State()
    confirm_update = State()
    update_status = State()
    confirm_status = State()
    update_location = State()
    confirm_location = State()
    menu = State()


init_data = {}


async def get_packages(dialog_manager: DialogManager, **kwargs):
    db: Session = next(get_db())
    user_tg_id = dialog_manager.event.from_user.id
    users = db.query(User).filter(User.telegram_id == user_tg_id).all()
    user = None
    packages = []
    try:
        user = users[0]
    except IndexError as e:
        set_error_log(db, user_tg_id, 0, "Нет пользователя")
    courier: Courier = user.courier
    if courier is None:
        set_warn_log(db, user_tg_id, 0, "Пользователь не курьер")
    else:
        packages = [
            {"id": package.package_id, "status": package.package_status, "location": package.current_location}
            for package in courier.packages
        ]

    # TODO Убрать, когда добавят связь пользователя с курьером
    # if len(packages) == 0:
    #     set_warn_log(db, user_tg_id, user.user_id, "Нет посылок у пользователя")
    #     packages = [
    #         {"id": 12345, "status": "TEST1", "location": "TEST1"},
    #         {"id": 2, "status": "TEST2", "location": "TEST2"}]

    data = {}
    for pack in packages:
        data[str(pack["id"])] = {item[0]: item[1] for item in packages[0].items() if item[0] != "id"}
    dialog_manager.dialog_data["packages"] = data
    return {"packages": packages}


async def confirm_update(c: CallbackQuery, button: Button, dialog_manager: DialogManager, package_id: str):
    package_status = dialog_manager.dialog_data["packages"][package_id]["status"]
    package_location = dialog_manager.dialog_data["packages"][package_id]["location"]
    dialog_manager.dialog_data["package_id"] = package_id
    dialog_manager.dialog_data["package_status"] = package_status
    dialog_manager.dialog_data["package_location"] = package_location
    init_data["package_id"] = package_id
    init_data["package_status"] = package_status
    init_data["package_location"] = package_location
    await dialog_manager.next()


async def update_data(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.next()


async def change_status(callback: CallbackQuery, widget: Any,
                        dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data["package_status"] = PackageStatusEnum[item_id]
    #print(type(dialog_manager.dialog_data["package_status"]))
    await dialog_manager.next()


async def change_location(message: Message, message_input: MessageInput,
                          dialog_manager: DialogManager):
    dialog_manager.dialog_data["package_location"] = message.text
    await dialog_manager.next()


async def cancel_change_status(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data["package_status"] = init_data["package_status"]
    await dialog_manager.next()


async def cancel_change_location(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data["package_location"] = init_data["package_location"]
    await dialog_manager.next()


async def save_update(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    db: Session = next(get_db())
    user_id = dialog_manager.event.from_user.id
    users = db.query(User).filter(User.telegram_id == user_id).all()
    user = None
    try:
        user = users[0]
    except IndexError as e:
        set_error_log(db, user_id, 0, "Нет пользователя")
    package_id = dialog_manager.dialog_data.get("package_id")
    new_status = dialog_manager.dialog_data.get("package_status")
    new_location = dialog_manager.dialog_data.get("package_location")
    if new_status != init_data["package_status"] or new_location != init_data["package_location"]:
        package = db.query(Package).filter(Package.package_id == package_id).first()
        if package:
            if new_status != init_data["package_status"]:
                package.package_status = new_status
            if new_location != init_data["package_location"]:
                package.current_location = new_location
            await c.message.answer(
                f"Посылка ID {package_id} успешно обновлена!\n"
            )
            set_info_log(db, user.telegram_id, user.user_id, "Курьер обновил информацию о доставляемой посылке")
        else:
            set_error_log(db, user.telegram_id, user.user_id, "Выбрана несуществующая посылка")
    else:
        await c.message.answer("Изменений не было.")
    await c.message.answer(
        f"Текущий СТАТУС: {new_status.value}\n"
        f"Текущая ЛОКАЦИЯ: {new_location}"
    )
    db.commit()
    await dialog_manager.done()
    await c.message.answer(text="В данный момент вы находитесь в меню заказчика.",
                           reply_markup=keyboards.user_menu())


async def cancel(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await c.message.answer(text="В данный момент вы находитесь в меню заказчика.",
                           reply_markup=keyboards.user_menu())


# Диалог
dialog = Dialog(
    # Шаг 1: Выбор посылки
    Window(
        Const("Выберите посылку:"),
        ScrollingGroup(
            Select(Format("ID: {item[id]}\nСТАТУС: {item[status].value}\nЛОКАЦИЯ: {item[location]}"),
                   id="scroll_packages",
                   item_id_getter=itemgetter("id"),
                   items="packages",
                   on_click=confirm_update
                   ),
            id="change_package",
            width=1,
            height=5
            # Button(Const("Далее"), id="next", on_click=confirm_update),
        ),
        Button(Const("❌ Выход/Отмена ❌"), id="close", on_click=cancel),
        state=ChangePackageStatus.package_selection,
        getter=get_packages
    ),
    # Шаг 2: Подтверждение обновления
    Window(
        Format("Хотите обновить данные для посылки ID \"{dialog_data[package_id]}\"?"),
        Row(
            Next(Const("Да ✅"), id="yes"),
            Back(Const("Нет ❌"), id="no"),
            id="row_accepting"
        ),
        Button(Const("❌ Выход/Отмена ❌"), id="close", on_click=cancel),
        state=ChangePackageStatus.confirm_update,
    ),
    # Шаг 3: Меню
    Window(
        Format(
            "Текущие СТАТУС \"{dialog_data[package_status].value}\" и ЛОКАЦИЯ \"{dialog_data[package_location]}\"."),
        SwitchTo(Const("Изменить СТАТУС 🤔"), id="update_status", state=ChangePackageStatus.update_status),
        SwitchTo(Const("Изменить ЛОКАЦИЮ 🤔"), id="update_location", state=ChangePackageStatus.update_location),
        Button(Const("✅ Сохранить ✅"), id="save", on_click=save_update),
        Button(Const("❌ Выход/Отмена ❌"), id="close", on_click=cancel),
        state=ChangePackageStatus.menu,
    ),
    # Шаг 4: Ввод СТАТУСА
    Window(
        Const("Выберете текущий СТАТУС:"),
        Group(
            Select(
                text=Format("{item.value}"),
                id="status_choice",
                items=list(PackageStatusEnum),
                item_id_getter=lambda item: item.name,
                on_click=change_status
            ),
            id="status_choice_group",
            width=1
        ),
        Row(
            Back(Const("⬅ Назад"), id="back"),
            SwitchTo(Const("Вперед ➡"), id="next", state=ChangePackageStatus.update_location),
            id="row_new_status"),
        Button(Const("❌ Выход/Отмена ❌"), id="close", on_click=cancel),
        SwitchTo((Const("🔝 Меню изменений 🔝")), id="menu", state=ChangePackageStatus.menu),
        state=ChangePackageStatus.update_status
    ),
    # Шаг 5: Подтверждение СТАТУСА
    Window(
        Format("Подтвердите СТАТУС \"{dialog_data[package_status].value}\":"),
        Group(
            Next(Const("✅ Подтверждаю ✅"), id="accept"),
            Button(Const("❌ Отменить изменение СТАТУСА ❌"), id="cancel_status_changing", on_click=cancel_change_status),
            id="row_accepting_status",
            width=1
        ),
        state=ChangePackageStatus.confirm_status,
    ),
    # Шаг 6: Ввод ЛОКАЦИИ
    Window(
        Const("Введите новую ЛОКАЦИЮ:"),
        Row(
            SwitchTo(Const("⬅ Назад"), id="back", state=ChangePackageStatus.update_status),
            SwitchTo(Const("Вперед ➡"), id="next", state=ChangePackageStatus.menu),
            id="row_new_location"),
        Button(Const("❌ Выход/Отмена ❌"), id="close", on_click=cancel),
        SwitchTo((Const("🔝 Меню изменений 🔝")), id="menu", state=ChangePackageStatus.menu),
        MessageInput(change_location),
        state=ChangePackageStatus.update_location
    ),
    # Шаг 7: Подтверждение ЛОКАЦИИ
    Window(
        Format("Подтвердите ЛОКАЦИЮ \"{dialog_data[package_location]}\":"),
        Group(
            SwitchTo(Const("✅ Подтверждаю ✅"), id="accept", state=ChangePackageStatus.menu),
            Button(Const("❌ Отменить изменение ЛОКАЦИИ ❌"), id="cancel_status_changing",
                   on_click=cancel_change_location),
            id="row_accepting_location",
            width=1
        ),
        state=ChangePackageStatus.confirm_location,
    ),
)

router.include_router(dialog)
setup_dialogs(router)


@router.callback_query(F.data == "package_choice")
async def package_choice(call: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(ChangePackageStatus.package_selection, mode=StartMode.RESET_STACK,
                               show_mode=ShowMode.EDIT)
