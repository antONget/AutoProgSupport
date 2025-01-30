from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import logging


def keyboard_pass_comment() -> InlineKeyboardMarkup:
    """
    Клавиатура для пропуска добавления комментария
    :return:
    """
    logging.info("keyboard_pass_comment")
    button_1 = InlineKeyboardButton(text='Пропустить', callback_data=f'pass_comment')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard


def keyboard_main_menu() -> ReplyKeyboardMarkup:
    """
    Клавиатура для открытия диалога с партнером
    :return:
    """
    logging.info("keyboard_finish_dialog_main_menu")
    button_1 = KeyboardButton(text='Главное меню')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]],
                                   resize_keyboard=True)
    return keyboard
