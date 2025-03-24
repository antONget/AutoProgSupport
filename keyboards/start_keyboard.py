from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from database.requests import UserRole, get_partners
from database.models import Partner
from filter.admin_filter import check_super_admin
import logging


async def keyboard_start(role: str, tg_id: int) -> ReplyKeyboardMarkup:
    """
    Стартовая клавиатура для каждой роли
    :param role:
    :param tg_id:
    :return:
    """
    logging.info("keyboard_start")
    keyboard = ''
    if role == UserRole.user:
        button_1 = KeyboardButton(text='Тарифы')
        button_2 = KeyboardButton(text='Задать вопрос')
        button_3 = KeyboardButton(text='Баланс')
        button_4 = KeyboardButton(text='FAQ')
        button_5 = KeyboardButton(text='Личный кабинет')
        list_partner: list[Partner] = await get_partners()
        if await check_super_admin(telegram_id=tg_id) or tg_id in list_partner:
            keyboard = ReplyKeyboardMarkup(keyboard=[[button_2], [button_3], [button_4], [button_5]],
                                           resize_keyboard=True)
        else:
            keyboard = ReplyKeyboardMarkup(keyboard=[[button_2], [button_3], [button_4]],
                                           resize_keyboard=True)
    elif role == UserRole.admin:
        button_1 = KeyboardButton(text='Партнеры')
        button_2 = KeyboardButton(text='Отчет')
        button_3 = KeyboardButton(text='Тарифы')
        button_5 = KeyboardButton(text='Вопросы')
        button_4 = KeyboardButton(text='Личный кабинет')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2], [button_3], [button_5], [button_4]],
                                       resize_keyboard=True)
    elif role == UserRole.partner:
        button_1 = KeyboardButton(text='Отчет')
        button_2 = KeyboardButton(text='Личный кабинет')
        button_3 = KeyboardButton(text='Вопросы')
        button_4 = KeyboardButton(text='FAQ')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2], [button_3], [button_4]], resize_keyboard=True)
    return keyboard


def keyboard_send_question() -> InlineKeyboardMarkup:
    logging.info("keyboard_send_question")
    button_1 = InlineKeyboardButton(text='Задать вопрос', callback_data=f'send_question')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard


def keyboard_change_role_admin() -> InlineKeyboardMarkup:
    logging.info("keyboard_change_role_admin")
    button_1 = InlineKeyboardButton(text='Изменить', callback_data=f'change_role_admin')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard


def keyboard_change_role_partner() -> InlineKeyboardMarkup:
    logging.info("keyboard_change_role_partner")
    button_1 = InlineKeyboardButton(text='Изменить', callback_data=f'change_role_partner')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard


def keyboard_select_role_admin() -> InlineKeyboardMarkup:
    logging.info("keyboard_select_role_admin")
    button_1 = InlineKeyboardButton(text='Администратор', callback_data=f'select_role_admin')
    button_2 = InlineKeyboardButton(text='Партнер', callback_data=f'select_role_partner')
    button_3 = InlineKeyboardButton(text='Пользователь', callback_data=f'select_role_user')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2], [button_3]])
    return keyboard


def keyboard_select_role_partner() -> InlineKeyboardMarkup:
    logging.info("keyboard_select_role_partner")
    button_2 = InlineKeyboardButton(text='Партнер', callback_data=f'select_role_partner')
    button_3 = InlineKeyboardButton(text='Пользователь', callback_data=f'select_role_user')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_3]])
    return keyboard


def keyboard_offer_agreement() -> InlineKeyboardMarkup:
    """
    Клавиатура для согласия с офертой
    [[Согласен]]
    :return:
    """
    logging.info("keyboard_offer_agreement")
    button_1 = InlineKeyboardButton(text='Согласен', callback_data=f'offer_agreement_confirm')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


# def keyboard_offer_agreement() -> InlineKeyboardMarkup:
#     logging.info("keyboard_offer_agreement")
#     button_1 = InlineKeyboardButton(text='Согласен', callback_data=f'offer_agreement_confirm')
#     button_2 = InlineKeyboardButton(text='Продолжить', callback_data=f'offer_agreement_continue')
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
#     return keyboard