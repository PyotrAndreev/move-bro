from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

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

def feedback_cancel_kb():
    kb_list = [
        [InlineKeyboardButton(text="❌ Отменить отправку", callback_data='cancel_feedback')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb_list)

def feedback_menu():
    kb_list = [
        [InlineKeyboardButton(text="Мои тикеты", callback_data='sent_feedback')],
        [InlineKeyboardButton(text="Написать нам", callback_data='feedback')],
        [InlineKeyboardButton(text="Вернуться", callback_data='cancel_feedback_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb_list)

def sent_feedback():
    kb_list = [
        [InlineKeyboardButton(text="Вернуться назад", callback_data='feedback_menu')],
        [InlineKeyboardButton(text="Вернуться в меню заказчика", callback_data='cancel_sent_feedback')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb_list)

def user_menu():
    kb_list = [
        [InlineKeyboardButton(text="Создать заявку на отправку", callback_data='create_request')],
        [InlineKeyboardButton(text="Отслеживать свои посылки", callback_data='track')],
        [InlineKeyboardButton(text="Посмортеть маршруты доставщиков", callback_data='find_journey')],
        [InlineKeyboardButton(text="Оставить отзыв", callback_data="feedback_menu")],
        [InlineKeyboardButton(text="Перейти в меню доставщика", callback_data="courier_menu")],
        [InlineKeyboardButton(text="Обратная связь", callback_data="feedback_menu")],
        [InlineKeyboardButton(text="📢Обязательно для ознакомления📢", callback_data="confirmation")],
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