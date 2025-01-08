from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging


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


def keyboard_partner_question(question_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для ответа или отклонения вопроса пользователя
    :return:
    """
    logging.info("keyboard_partner_question")
    button_1 = InlineKeyboardButton(text='Взять', callback_data=f'question_attach_{question_id}')
    button_2 = InlineKeyboardButton(text='Отклонить', callback_data=f'question_reject_{question_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard
