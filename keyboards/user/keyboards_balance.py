from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging


def keyboard_replenish_balance() -> InlineKeyboardMarkup:
    """
    Пополнение баланса
    :return:
    """
    logging.info("keyboard_replenish_balance")
    button_1 = InlineKeyboardButton(text='Пополнить баланс', callback_data='replenish_balance')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_payment(payment_url: str, payment_id: int, amount: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для проведения и проверки платежа
    :param payment_url:
    :param payment_id:
    :param amount:
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = InlineKeyboardButton(text='Продолжить', callback_data=f'pay_replenish_{amount}_{payment_id}')
    button_2 = InlineKeyboardButton(text=f'Пополнить баланс на {amount} руб.', url=payment_url)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard