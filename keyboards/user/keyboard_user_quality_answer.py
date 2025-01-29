from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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
