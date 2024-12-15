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
        [InlineKeyboardButton(text="Назад", callback_data='cancel')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def cancel_and_skip_data():
    kb_list = [
        [InlineKeyboardButton(text="Назад", callback_data='cancel')],
        [InlineKeyboardButton(text="Пропустить", callback_data='skip')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def user_menu():
    kb_list = [
        [InlineKeyboardButton(text="Создать заявку на отправку", callback_data='create_request')],
        [InlineKeyboardButton(text="Отслеживать посылки", callback_data='track')],
        [InlineKeyboardButton(text="Каталог посылок", callback_data="orders_catalogue")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard