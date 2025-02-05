from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def keyboard_select_action_rate() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора роли для редактирования
    :return:
    """
    logging.info('keyboard_select_role')
    button_1 = InlineKeyboardButton(text='Добавить',
                                    callback_data='rate_action_add')
    button_2 = InlineKeyboardButton(text='Удалить',
                                    callback_data='rate_action_del')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboards_del_rate(list_rate: list) -> InlineKeyboardMarkup:
    """
    Клавиатура для удаления тарифа
    :param list_rate:
    :return:
    """
    logging.info(f'keyboards_del_rate')
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for rate in list_rate:
        text = rate.title_rate
        button = f'rate_select_del_{rate.id}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()
