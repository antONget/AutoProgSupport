from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
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


def keyboard_partner_begin_question(question_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для ответа или отклонения вопроса пользователя
    :return:
    """
    logging.info("keyboard_partner_question")
    button_1 = InlineKeyboardButton(text='Указать стоимость', callback_data=f'question_cost_{question_id}')
    button_2 = InlineKeyboardButton(text='Отказаться', callback_data=f'question_reject_{question_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard