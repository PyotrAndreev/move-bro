from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram_dialog import Dialog, ShowMode, StartMode
from aiogram.types import FSInputFile
from TelegramBot.keyboards import keyboards

router = Router()

class PdfForm(StatesGroup):
    show_pdf = State()

async def on_get_pdf_click(c: CallbackQuery, button: Button, manager: DialogManager):
    await c.message.delete()
    await c.message.answer_document(
        FSInputFile("TelegramBot/useful/confirmation.pdf"),
        caption="Вот ваш PDF-документ 📄"
    )
    await c.message.answer(
        text="Меню заказчика:",
        reply_markup=keyboards.user_menu()
    )
    await manager.done()

pdf_window = Window(
    Const("Перед началом пользования ботом в обязательном порядке нужно ознакомиться с правилами пользования"),
    Button(Const("📄 Получить документ"), id="get_pdf", on_click=on_get_pdf_click),
    state=PdfForm.show_pdf,
)

dialog = Dialog(pdf_window)

router.include_router(dialog)

@router.callback_query(F.data == "confirmation") 
async def start_choosing(call: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(PdfForm.show_pdf, mode=StartMode.RESET_STACK)