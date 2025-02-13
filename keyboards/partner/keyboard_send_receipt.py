from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging


def keyboard_payment_receipt(payment_url: str,
                             payment_id: int,
                             amount: str,
                             id_question: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для выставления счета
    :param payment_url:
    :param payment_id:
    :param amount:
    :param id_question:
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = InlineKeyboardButton(text='Продолжить', callback_data=f'sendreceipt_{id_question}_{payment_id}')
    button_2 = InlineKeyboardButton(text=f'Оплатить {amount} руб.', url=payment_url)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard


def keyboard_payment_receipt_balance(payment_url: str,
                                     payment_id: int,
                                     amount: str,
                                     id_question: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для выставления счета
    :param payment_url:
    :param payment_id:
    :param amount:
    :param id_question:
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = InlineKeyboardButton(text='Продолжить', callback_data=f'sendreceipt_{amount}_{id_question}_{payment_id}')
    button_2 = InlineKeyboardButton(text=f'Оплатить {amount} руб.', url=payment_url)
    button_3 = InlineKeyboardButton(text='Списать с баланса', callback_data=f'debited_{amount}_{id_question}_{payment_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1], [button_3]],)
    return keyboard
