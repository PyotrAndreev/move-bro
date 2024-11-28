from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

def get_ready():
    kb_list = [
        [InlineKeyboardButton(text="Начать", callback_data='get_ready')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def gender_kb():
    kb_list = [
        [InlineKeyboardButton(text="Мужчина", callback_data='man')],
        [InlineKeyboardButton(text="Женщина", callback_data='woman')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def check_data():
    kb_list = [
        [InlineKeyboardButton(text="✅Все верно", callback_data='correct')],
        [InlineKeyboardButton(text="❌Заполнить сначала", callback_data='incorrect')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def cancel_data():
    kb_list = [
        [KeyboardButton(text="Назад")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list,
                                   resize_keyboard=True,
                                   one_time_keyboard=True)
    return keyboard

def cancel_and_skip_data():
    kb_list = [
        [KeyboardButton(text="Назад")],
        [KeyboardButton(text="Пропустить")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list,
                                   resize_keyboard=True,
                                   one_time_keyboard=True)
    return keyboard

def user_menu():
    kb_list = [[KeyboardButton(text="Создать заявку на отправку")],
               [KeyboardButton(text="Отслеживать посылки")],
               [KeyboardButton(text="Каталог посылок")],
               [KeyboardButton(text="Помощь")],]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list,
                                   resize_keyboard=True,
                                   one_time_keyboard=True)
    return keyboard