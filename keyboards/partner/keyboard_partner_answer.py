from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging


# def keyboard_send() -> InlineKeyboardMarkup:
#     """
#     Клавиатура для добавления материала к вопросу
#     :return:
#     """
#     logging.info("keyboard_send")
#     button_1 = InlineKeyboardButton(text='Отправить', callback_data=f'send_content')
#     button_2 = InlineKeyboardButton(text='Добавить', callback_data=f'add_content')
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
#     return keyboard
#
#
# def keyboard_partner_question(question_id: int) -> InlineKeyboardMarkup:
#     """
#     Клавиатура для ответа или отклонения вопроса пользователя
#     :return:
#     """
#     logging.info("keyboard_partner_question")
#     button_1 = InlineKeyboardButton(text='Взять', callback_data=f'question_attach_{question_id}')
#     button_2 = InlineKeyboardButton(text='Отклонить', callback_data=f'question_reject_{question_id}')
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
#     return keyboard


def keyboard_partner_reject(question_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для отклонения вопроса пользователя после того как его взял
    :return:
    """
    logging.info("keyboard_partner_reject")
    button_1 = InlineKeyboardButton(text='Отклонить', callback_data=f'question_reject_{question_id}')
    button_2 = InlineKeyboardButton(text='Заявка выполнена', callback_data=f'question_completed_{question_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1], [button_2]],)
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