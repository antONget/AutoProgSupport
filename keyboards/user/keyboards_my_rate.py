from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import Rate
import logging


def keyboard_ask_typy() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора направления для ответа
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = InlineKeyboardButton(text='Спросить у ИИ', callback_data=f'ask_artificial_intelligence')
    button_2 = InlineKeyboardButton(text=f'Задать вопрос специалисту', callback_data=f'ask_master')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard


def keyboard_ask_master() -> ReplyKeyboardMarkup:
    """
    Клавиатура для открытия диалога с партнером
    :return:
    """
    logging.info("keyboard_finish_dialog_main_menu")
    button_1 = KeyboardButton(text='Задать вопрос специалисту')
    button_2 = KeyboardButton(text='Главное меню')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]],
                                   resize_keyboard=True)
    return keyboard
