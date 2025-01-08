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
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]], resize_keyboard=True)
    elif role == UserRole.admin:
        button_1 = KeyboardButton(text='Партнеры')
        button_2 = KeyboardButton(text='Отчет')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]], resize_keyboard=True)
    elif role == UserRole.partner:
        button_1 = KeyboardButton(text='Отчет')
        keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]], resize_keyboard=True)
    return keyboard


def keyboard_send_question() -> InlineKeyboardMarkup:
    logging.info("keyboard_send_question")
    button_1 = InlineKeyboardButton(text='Задать вопрос', callback_data=f'send_question')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]],)
    return keyboard
