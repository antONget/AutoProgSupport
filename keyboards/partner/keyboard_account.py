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
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard

