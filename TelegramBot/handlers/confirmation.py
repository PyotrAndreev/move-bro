from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram_dialog import Dialog, ShowMode, StartMode

router = Router()

class Form(StatesGroup):
    show_pdf = State()

# 4. Определяем окно диалога
pdf_window = Window(
    Const("Обязательно ознакомьтесь с данным документом!!!"),
    state=Form.show_pdf
)

dialog = Dialog(pdf_window)

@router.callback_query(F.data == "confirmation") 
async def start_choosing(call: CallbackQuery, dialog_manager: DialogManager):
    await dialog_manager.start(Form.show_pdf, mode=StartMode.RESET_STACK)
    pdf = InputFile('TelegramBot/useful/confirmation.pdf')
    await dialog_manager.bot.send_document(
        chat_id=dialog_manager.event.from_user.id,
        document=pdf,
        caption="Пожалуйста, ознакомьтесь с этим документом PDF."
    )
