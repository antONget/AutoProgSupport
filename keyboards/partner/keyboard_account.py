from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models import User, Partner
from database import requests as rq
from filter.admin_filter import check_super_admin
import logging


async def keyboard_partner_account(info_partner: User) -> InlineKeyboardMarkup:
    """
    Клавиатура для правки обращения к партнеру
    :return:
    """
    logging.info("keyboard_partner_account")
    if info_partner.fullname != "none":
        name_text = info_partner.fullname
    else:
        name_text = f"специалист #_{info_partner.id}"
    list_partner: list[Partner] = await rq.get_partners()
    if await check_super_admin(telegram_id=info_partner.tg_id):
        role = rq.UserRole.admin
    elif info_partner.tg_id in list_partner:
        role = rq.UserRole.partner
    button_1 = InlineKeyboardButton(text=f'Имя-{name_text}', callback_data=f'fullname_{info_partner.id}')
    button_2 = InlineKeyboardButton(text=f'Сменить роль', callback_data=f'change_role_{role}')
    button_3 = InlineKeyboardButton(text=f'Баланс', callback_data=f'balancepartner_{info_partner.id}')
    button_4 = InlineKeyboardButton(text='Запросить вывод средств', callback_data='request_withdrawal_funds')
    button_5 = InlineKeyboardButton(text='Рейтинг ⭐️', callback_data=f'rating_partner')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3], [button_4], [button_5]])
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
