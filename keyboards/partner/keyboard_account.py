from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models import User
import logging


def keyboard_partner_account(info_partner: User) -> InlineKeyboardMarkup:
    """
    Клавиатура для правки обращения к партнеру
    :return:
    """
    logging.info("keyboard_partner_account")
    if info_partner.fullname != "none":
        name_text = info_partner.fullname
    else:
        name_text = f"специалист #_{info_partner.id}"
    button_1 = InlineKeyboardButton(text=f'Имя-{name_text}', callback_data=f'fullname_{info_partner.id}')
    button_2 = InlineKeyboardButton(text=f'Баланс', callback_data=f'balancepartner_{info_partner.id}')
    button_3 = InlineKeyboardButton(text='Запросить вывод средств', callback_data='request_withdrawal_funds')
    button_4 = InlineKeyboardButton(text='Рейтинг ⭐️', callback_data=f'rating_partner')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4]])
    return keyboard


def keyboard_request_withdrawal_funds(id_: int, summ_funds: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для подтверждения вывода средств партнеру
    :return:
    """
    logging.info("keyboard_request_withdrawal_funds")
    button_1 = InlineKeyboardButton(text=f'Списать {summ_funds} ₽',
                                    callback_data=f'withdrawalfunds_confirm_{id_}_{summ_funds}')
    button_2 = InlineKeyboardButton(text=f'Отклонить',
                                    callback_data=f'withdrawalfunds_cancel_{id_}_{summ_funds}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard
