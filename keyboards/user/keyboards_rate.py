from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import Rate
import logging


def keyboards_select_rate(list_rate: list[Rate]) -> InlineKeyboardMarkup:
    """
    Клавиатура с пагинацией для добавления персонала
    :param list_rate:
    :return:
    """
    logging.info(f'keyboards_select_rate')
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for rate in list_rate:
        text_button = rate.title_rate
        callback_button = f'select_rate_{rate.id}'
        buttons.append(InlineKeyboardButton(
            text=text_button,
            callback_data=callback_button))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()


def keyboard_payment(payment_url: str, payment_id: int, amount: str, rate_id: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для проведения и проверки платежа
    :param payment_url:
    :param payment_id:
    :param amount:
    :param rate_id:
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = InlineKeyboardButton(text='Задать вопрос', callback_data=f'payment_{rate_id}_{payment_id}')
    button_2 = InlineKeyboardButton(text=f'Оплатить {amount} руб.', url=payment_url)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard


def keyboard_send_question() -> InlineKeyboardMarkup:
    logging.info("keyboard_send_question")
    button_1 = InlineKeyboardButton(text='Задать вопрос', callback_data=f'send_question')
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
