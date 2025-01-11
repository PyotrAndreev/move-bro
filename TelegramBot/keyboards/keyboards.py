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
        [InlineKeyboardButton(text="Каталог посылок", callback_data="orders_catalogue")],
        [InlineKeyboardButton(text="Доставляемые посылки", callback_data="package_choice")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

'''def user_menu(data, first, last, page):
    kb_list = []
    if not first:
        kb_list.append([InlineKeyboardButton(text="Назад", callback_data='prev')])
    for i in range(0, len(data)):
        kb_list.append([InlineKeyboardButton(text=str(page + i) + ") Адресат: " + str(data[i].recipient_name) + " | Откуда: " + str(data[i].shipping_city) + " | Куда: " + str(data[i].delivery_city) + " | Цена доставки: " + str(data[i].cost),
                                             callback_data="request_" + str(i + 1))])
    if not last:
        kb_list.append([InlineKeyboardButton(text="Вперед", callback_data='next')])
    kb_list.append([InlineKeyboardButton(text="Вернуться в меню", callback_data='to_menu')])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard'''