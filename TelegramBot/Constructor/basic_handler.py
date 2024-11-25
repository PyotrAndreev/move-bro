from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, KeyboardButton, \
    ReplyKeyboardMarkup
from aiogram.utils.formatting import Bold, Text
# Создаём router
router = Router()
# Клавиатуры
# Inline-клавиатура(красивые кнопки под сообщением)
kb_list = [
        # text - то, что написано в кнопке, callback_data - можно сказать ID кнопки, по которой мы её сможем обработать
        [InlineKeyboardButton(text="Перейти в меню", callback_data='menu')]
    ]
# Прикрепляем к inline_keyboard кнопки из kb_list
inline_keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
# Обычная клавиатура(ReplyKeyboard, раскрывается, если отправить сообщение с прикреплённой клавиатурой или по нажатию кнопки в строке набора сообщения)
kb_list = [
        [KeyboardButton(text="Кнопка1")], [KeyboardButton(text="Кнопка2")]
    ]
# keyboard - прикрепляем кнопки, resize_keyboard - определяем размер кнопок в зависимости от длины текста,
# one_time_keyboard - клавиатура скроется после нажатия кнопки / после того, как бот отправит следующее сообщение, чтобы открыть её снова, нужно нажать на кнопку в строке набора сообщения
# input_field_placeholder - строка, которая будет отображаться в строке набора сообщения(как подсказка в формах, типо бледный текст "введите здесь свою почту" в поле ввода)
reply_keyboard = ReplyKeyboardMarkup(keyboard=kb_list,
                               resize_keyboard=True,
                               one_time_keyboard=True,
                               input_field_placeholder="Выбери кнопку:")
# Можем обрабатывать команды(например, /register)
@router.message(Command("register"))
async def cmd_register(message: Message):
    # reply_markup - какую клавиатуру мы отправим (Inline или обычную)
    await message.answer("Привет! Мы тебя зарегистрировали", reply_markup=inline_keyboard)
# Можем обрабатывать inline-кнопки(красивые кнопки, которые расположены под сообщением)
@router.callback_query(F.data=="callback_test")
async def callback_button_test(call: CallbackQuery):
    await call.message.answer("Ты нажал на красивую кнопку! Получай другие кнопки!", reply_markup=reply_keyboard)
# Можем обрабатывать обычные кнопки(отправляются как сообщение, поэтому обрабатываем её как сообщение)
@router.message(F.text=="Кнопка1")
async def simple_button(message: Message):
    await message.answer("Ты нажал на кнопку1!")
