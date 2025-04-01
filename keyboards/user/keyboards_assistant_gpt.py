from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import Rate
import logging


def keyboard_ask_typy() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора направления для ответа
    :return:
    """
    logging.info("keyboard_payment")
    button_1 = InlineKeyboardButton(text='Помощник AUTO PROG', callback_data=f'ask_artificial_intelligence')
    button_2 = InlineKeyboardButton(text=f'Задать вопрос специалисту', callback_data=f'ask_master')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard


def keyboard_ask_master() -> ReplyKeyboardMarkup:
    """
    Клавиатура для открытия диалога с партнером
    :return:
    """
    logging.info("keyboard_finish_dialog_main_menu")
    button_1 = KeyboardButton(text='Задать вопрос специалисту')
    button_2 = KeyboardButton(text='Главное меню')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1], [button_2]],
                                   resize_keyboard=True)
    return keyboard


def keyboard_period_gpt() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора периода доступа к ИИ
    :return:
    """
    logging.info("keyboard_send")
    button_1 = InlineKeyboardButton(text='Неделя 300 ₽', callback_data=f'period_payment_gpt_week')
    button_2 = InlineKeyboardButton(text='Месяц 1000 ₽', callback_data=f'period_payment_gpt_month')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard


def keyboard_send() -> InlineKeyboardMarkup:
    """
    Клавиатура для добавления материала к вопросу
    :return:
    """
    logging.info("keyboard_send")
    button_1 = InlineKeyboardButton(text='Отправить', callback_data=f'send_content')
    button_2 = InlineKeyboardButton(text='Добавить', callback_data=f'add_content')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard


def keyboard_payment_gpt(payment_url: str, payment_id: int, amount: str, period: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для проведения и проверки платежа
    :param payment_url:
    :param payment_id:
    :param amount:
    :param period:
    :return:
    """
    logging.info("keyboard_payment_gpt")
    button_1 = InlineKeyboardButton(text='Продолжить', callback_data=f'gptpayment_{period}_{payment_id}')
    button_2 = InlineKeyboardButton(text=f'Оплатить {amount} руб.', url=payment_url)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard


def keyboard_main_menu() -> ReplyKeyboardMarkup:
    """
    Клавиатура для открытия диалога с партнером
    :return:
    """
    logging.info("keyboard_finish_dialog_main_menu")
    button_1 = KeyboardButton(text='Главное меню')
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]],
                                   resize_keyboard=True)
    return keyboard