from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
import logging


def keyboard_payment_user_question(payment_url: str,
                                   payment_id: int, amount: str, id_question: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для проведения и проверки платежа
    :param payment_url:
    :param payment_id:
    :param amount:
    :param id_question:
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = InlineKeyboardButton(text='Продолжить', callback_data=f'payquestion_{id_question}_{payment_id}')
    button_2 = InlineKeyboardButton(text=f'Оплатить {amount} руб.', url=payment_url)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard


def keyboard_payment(payment_url: str,
                     payment_id: int,
                     amount: str,
                     id_question: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для проведения и проверки платежа
    :param payment_url:
    :param payment_id:
    :param amount:
    :param id_question:
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = InlineKeyboardButton(text='Продолжить', callback_data=f'payquestion_{id_question}_{payment_id}')
    button_2 = InlineKeyboardButton(text=f'Оплатить {amount} руб.', url=payment_url)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard


def keyboard_open_dialog_partner(id_question: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для открытия диалога с партнером
    :param id_question:
    :return:
    """
    logging.info("keyboard_open_dialog_partner")
    button_1 = InlineKeyboardButton(text='Написать специалисту', callback_data=f'open_dialog_partner_{id_question}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_open_dialog_user(id_question: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для открытия диалога с партнером
    :param id_question:
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = InlineKeyboardButton(text='Написать пользователю', callback_data=f'open_dialog_user_{id_question}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_finish_dialog() -> ReplyKeyboardMarkup:
    """
    Клавиатура для открытия диалога с партнером
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = KeyboardButton(text='Завершить диалог')
    button_2 = KeyboardButton(text='Главное меню')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]],
                                   resize_keyboard=True)
    return keyboard


def keyboard_finish_dialog_partner() -> ReplyKeyboardMarkup:
    """
    Клавиатура для открытия диалога с партнером
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = KeyboardButton(text='Завершить диалог')
    button_2 = KeyboardButton(text='Выставить_счет')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]],
                                   resize_keyboard=True)
    return keyboard


def keyboard_finish_dialog_main_menu() -> ReplyKeyboardMarkup:
    """
    Клавиатура для открытия диалога с партнером
    :return:
    """
    logging.info("keyboard_finish_dialog_main_menu")
    button_1 = KeyboardButton(text='Главное меню')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]],
                                   resize_keyboard=True)
    return keyboard


def keyboard_quality_answer(question_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для оценки качества ответа
    :return:
    """
    logging.info("keyboard_partner_reject")
    button_1 = InlineKeyboardButton(text='⭐⭐⭐⭐⭐', callback_data=f'quality_5_{question_id}')
    button_2 = InlineKeyboardButton(text='⭐⭐⭐⭐', callback_data=f'quality_4_{question_id}')
    button_3 = InlineKeyboardButton(text='⭐⭐⭐', callback_data=f'quality_3_{question_id}')
    button_4 = InlineKeyboardButton(text='⭐⭐', callback_data=f'quality_2_{question_id}')
    button_5 = InlineKeyboardButton(text='⭐', callback_data=f'quality_1_{question_id}')
    button_6 = InlineKeyboardButton(text='Вопрос не решен', callback_data=f'quality_0_{question_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2],
                                                     [button_3], [button_4],
                                                     [button_5], [button_6]],)
    return keyboard
