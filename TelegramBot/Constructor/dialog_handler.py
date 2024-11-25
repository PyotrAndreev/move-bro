from typing import Any

from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import DialogManager, Window, setup_dialogs, StartMode
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from TelegramBot.data_base import User, Package
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog
# Старый добрый router
router = Router()
# Делаем форму orders_catalogue, записываем в неё шаги
class orders_catalogue(StatesGroup):
    # Шаг 1: выбор заказов из списка
    choosing_orders = State()
# Шаг 1 выдаёт список, для списка нужна функция getter, которая вернёт нам элементы списка
async def orders_getter(dialog_manager: DialogManager):
    # Представим, что packages были получены из БД
    packages = [{'package_id':1, 'delivery_city': 'Московия', 'sender_contacts':'tg: @ayesha, phone: 79995476677'}]
    return {
        'packages': packages
    }
# Функция on_order_selected обрабатывает выбранный элемент списка(item)
async def on_order_selected(callback: CallbackQuery, widget: Any,
                            manager: DialogManager, item: Package):
    # Записываем в данные формы выбранную посылку
    manager.dialog_data['package'] = item
    # Переключаем пользователя на следующий шаг(шаг 2)
    await manager.next()
# Окно шага 1: Состоит из текста сообщения (Const) и списка(ScrollingGroup, делает список с помощью Inline-кнопок)
# Элементы списка - объекты Select
# Что по Select:
# Format - отвечает за надпись на Inline-кнопке(берёт её из item - объекта переданного списка
# id - id списка(?), можно вообще рандомную строку написать и будет норм
# items - нам getter даёт словарь, выбираем, по чему из словаря итерироваться
# item_id_getter - что мы передаём функции, обрабатывающей клик на выбранный элемент списка(может быть id элемента в БД, мы же не стали
# заморачиваться и передали объект целиком
# on_click - функция, которая обрабатывает клик на выбранный элемент, ей передаётся объект, который вернула функция из item_id_getter
# Идём дальше, что ещё по ScrollingGroup:
# width - сколько кнопок будет в одной строке
# height - сколько кнопок будет в одном столбце(если объектов больше, то aiogram_dialog добавит удобные стрелочки для пролистывания списка
# id - id ScrollingGroup(?), не пробовал менять, лучше оставить так же, как и здесь ('scroll_with_pager')
# Идём к Window:
# getter - функция, которая записывает в данные формы то, что вернула функция getter
# state - указывает, к какому шагу формы относится окно (к шагу 1 - выбор заказа (choosing_orders))
orders_choose = Window(
    Const('Выбери интересующий заказ из списка'),
    ScrollingGroup(
        Select(
            Format("{item[delivery_city]}"),
            id='s_orders',
            items='packages',
            item_id_getter=lambda x:x,
            on_click=on_order_selected,
        ),
        width=1,
        height=5,
        id='scroll_with_pager'
    ),
    getter=orders_getter,
    state=orders_catalogue.choosing_orders
)
# Dialog - полная форма, в неё передаём все шаги
orders_choose_dialog = Dialog(orders_choose)
# Dialog можно скастовать к router(?), а ещё Dialog обрабатывает события, относящиеся к форме, поэтому нужно добавить его к остальным router
router.include_router(orders_choose_dialog)
# Функция setup_dialogs настраивает все Dialog, ей нужно передать router/dispatcher
setup_dialogs(router)
# Нажали на кнопку выбора заказов
@router.callback_query(F.data=="orders_catalogue")
# так как кнопка запускает форму, передаём ей DialogManager, который отвечает за запуск формы
async def start_questionnaire_process(call: CallbackQuery, dialog_manager: DialogManager):
    # Говорим DialogManager, чтобы он запустил формы с шага выбора заказов (orders_catalogue.choosing_orders
    # mode=StartMode.RESET_STACK означает, что несколько форм одновременно заполняться не могут и нужно удалить старые незаполненные формы
    await dialog_manager.start(orders_catalogue.choosing_orders, mode=StartMode.RESET_STACK)