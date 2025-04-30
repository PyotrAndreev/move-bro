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
    Row,
    Button, Back
)
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy.orm import Session
from asyncio import sleep, create_task

from TelegramBot.data_base import User, Courier, Courier_Request, get_db

from TelegramBot.logging_helper import set_info_log

router = Router()

class CreateJourneyForm(StatesGroup):
    shipping_country = State()
    shipping_state = State()
    shipping_city = State()
    delivery_country = State()
    delivery_state = State()
    delivery_city = State()
    comment = State()
    check_process = State()

async def get_form_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data
    return {
        "shipping_country": data.get("shipping_country"),
        "shipping_state": data.get("shipping_state"),
        "shipping_city": data.get("shipping_city"),
        "delivery_country": data.get("delivery_country"),
        "delivery_state": data.get("delivery_state"),
        "delivery_city": data.get("delivery_city"),
        "comment": data.get("comment"),
    }

async def get_safe_form_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.dialog_data

    def safe_val(key):
        val = data.get(key)
        return val if val is not None else "-"
    
    return {
        "shipping_country": safe_val("shipping_country"),
        "shipping_state": safe_val("shipping_state"),
        "shipping_city": safe_val("shipping_city"),
        "delivery_country": safe_val("delivery_country"),
        "delivery_state": safe_val("delivery_state"),
        "delivery_city": safe_val("delivery_city"),
        "comment": safe_val("comment"),
    }

async def back_to_menu(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    from TelegramBot.handlers.courier_menu import CourierMenuStates

    await manager.start(CourierMenuStates.choosing_menu, mode=StartMode.RESET_STACK)

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






async def magic_button(
    callback_query: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    manager.dialog_data['shipping_country'] = "Russia"
    manager.dialog_data['shipping_state'] = "Arizona"
    manager.dialog_data['shipping_city'] = "Gamburg"
    manager.dialog_data['delivery_country'] = "Canada"
    manager.dialog_data['delivery_state'] = "Novosibirskaya oblast"
    manager.dialog_data['delivery_city'] = "Dubai"
    manager.dialog_data['comment'] = "LOL"
    await manager.switch_to(CreateJourneyForm.check_process, show_mode=ShowMode.EDIT)





async def on_comment_changed(
    message: Message, dialog: MessageInput, manager: DialogManager
):
    await message.delete()
    manager.dialog_data["comment"] = message.text
    await manager.next(show_mode=ShowMode.EDIT)

async def on_restart_clicked(callback_query: CallbackQuery, button: Button, manager: DialogManager):
    await manager.done()
    await callback_query.message.delete()
    await manager.start(CreateJourneyForm.shipping_country, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT)

async def on_finish_clicked(
    callback_query: CallbackQuery, button: Button, manager: DialogManager
):
    from TelegramBot.handlers.courier_menu import CourierMenuStates

    chat_id = callback_query.message.chat.id
    await callback_query.message.delete()
    db: Session = next(get_db())
    user_tg_id = callback_query.from_user.id
    user: User = db.query(User).filter(User.telegram_id == user_tg_id).first()
    courier: Courier = user.courier
    if courier is None:
        courier: Courier = Courier(user=user)
        db.add(courier)
        db.commit()
    data = await get_form_data(manager)
    courier_request = Courier_Request(
        shipping_country=data.get("shipping_country"),
        shipping_state=data.get("shipping_state"),
        shipping_city=data.get("shipping_city"),
        delivery_country=data.get("delivery_country"),
        delivery_state=data.get("delivery_state"),
        delivery_city=data.get("delivery_city"),
        comment=data.get("comment"),
        courier=courier
    )
    db.add(courier_request)
    db.commit()

    set_info_log(db, user_tg_id, courier.courier_id, f"Создана заявка курьера {courier_request.courier_request_id}")

    message = await callback_query.bot.send_message(chat_id, text="Заявка успешно создана!")
    create_task(delete_message_after_time(callback_query, manager, message))
    await manager.done()
    await manager.start(CourierMenuStates.choosing_menu, mode=StartMode.RESET_STACK)

async def delete_message_after_time(
    callback_query: CallbackQuery, manager: DialogManager, message
):
    await sleep(5)
    try:
        await callback_query.bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass

dialog = Dialog(
    Window(
        Const("Данные по месту отправки"),
        Const("Введите страну:"),
        MessageInput(on_shipping_country_changed),
        Button(Const("Тестовый пример"), id="magic_button", on_click=magic_button),
        Button(Const("Назад"), id="back_to_menu", on_click=back_to_menu),
        state=CreateJourneyForm.shipping_country,
    ),
    Window(
        Const("Данные по месту отправки"),
        Const("Введите штат/область/округ(и т.д.):"),
        MessageInput(on_shipping_state_changed, filter=~F.text.lower().in_(["пропустить"])),
        Row(
            Button(Const("Пропустить"), "skip", on_click=lambda c, b, m: m.next()),
            Back(Const("Назад"), show_mode=ShowMode.EDIT),
        ),
        state=CreateJourneyForm.shipping_state,
    ),
    Window(
        Const("Данные по месту отправки"),
        Const("Введите город:"),
        MessageInput(on_shipping_city_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=CreateJourneyForm.shipping_city,
    ),
    Window(
        Const("Данные по месту назначения"),
        Const("Введите страну:"),
        MessageInput(on_delivery_country_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=CreateJourneyForm.delivery_country,
    ),
    Window(
        Const("Данные по месту назначения"),
        Const("Введите штат/область/округ(и т.д.):"),
        MessageInput(on_delivery_state_changed, filter=~F.text.lower().in_(["пропустить"])),
        Row(
            Button(Const("Пропустить"), "skip", on_click=lambda c, b, m: m.next()),
            Back(Const("Назад"), show_mode=ShowMode.EDIT),
        ),
        state=CreateJourneyForm.delivery_state,
    ),
    Window(
        Const("Данные по месту назначения"),
        Const("Введите город:"),
        MessageInput(on_delivery_city_changed),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=CreateJourneyForm.delivery_city,
    ),
    Window(
        Const("Оставьте комментарий:"),
        MessageInput(on_comment_changed),
        Button(Const("Пропустить"), "skip", on_click=lambda c, b, m: m.next()),
        Back(Const("Назад"), show_mode=ShowMode.EDIT),
        state=CreateJourneyForm.comment,
    ),
    Window(
        Format(
            "Все данные заполнены!\n"
            "Пожалуйста, проверьте все ли верно:\n"
            "<b>Адрес отправки</b>: {shipping_country}, {shipping_state}, {shipping_city}\n"
            "<b>Адрес доставки</b>: {delivery_country}, {delivery_state}, {delivery_city}\n"
            "<b>Комментарий</b>: {comment}"
        ),
        Button(Const("Все верно"), id="finish", on_click=on_finish_clicked),
        Button(Const("Неверно, начать сначала"), id="restart", on_click=on_restart_clicked),
        Back(Const('Назад'), show_mode=ShowMode.EDIT),
        parse_mode="HTML",
        state=CreateJourneyForm.check_process,
        getter=get_safe_form_data,
    ),
)

router.include_router(dialog)
@router.callback_query(F.data == "create_request")
async def start_request_process(
    callback_query: CallbackQuery, dialog_manager: DialogManager
):
    await dialog_manager.start(
        CreateJourneyForm.shipping_country, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT
    )