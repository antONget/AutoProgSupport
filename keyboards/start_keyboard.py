from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from database.requests import UserRole
import logging


def keyboard_start(role: str) -> ReplyKeyboardMarkup:
    """
    Стартовая клавиатура для каждой роли
    :param role:
    :return:
    """
    logging.info("keyboard_start")
    keyboard = ''
    if role == UserRole.user:
        button_1 = KeyboardButton(text='Тарифы')
        button_2 = KeyboardButton(text='Задать вопрос')
        button_3 = KeyboardButton(text='Баланс')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2], [button_3]], resize_keyboard=True)
    elif role == UserRole.admin:
        button_1 = KeyboardButton(text='Партнеры')
        button_2 = KeyboardButton(text='Отчет')
        button_3 = KeyboardButton(text='Тарифы')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2], [button_3]],
                                       resize_keyboard=True)
    elif role == UserRole.partner:
        button_1 = KeyboardButton(text='Отчет')
        button_2 = KeyboardButton(text='Личный кабинет')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]], resize_keyboard=True)
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
    logging.info("keyboard_offer_agreement")
    button_1 = InlineKeyboardButton(text='Согласен', callback_data=f'offer_agreement_confirm')
    button_2 = InlineKeyboardButton(text='Продолжить', callback_data=f'offer_agreement_continue')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard


def keyboard_offer_agreement() -> InlineKeyboardMarkup:
    logging.info("keyboard_offer_agreement")
    button_1 = InlineKeyboardButton(text='Согласен', callback_data=f'offer_agreement_confirm')
    button_2 = InlineKeyboardButton(text='Продолжить', callback_data=f'offer_agreement_continue')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]])
    return keyboard