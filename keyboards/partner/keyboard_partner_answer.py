from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging


def keyboard_partner_continue_question(question_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для ответа или отклонения вопроса пользователя
    :return:
    """
    logging.info("keyboard_partner_question")
    button_1 = InlineKeyboardButton(text='Указать стоимость', callback_data=f'question_cost_{question_id}')
    button_2 = InlineKeyboardButton(text='Отказаться', callback_data=f'question_reject_{question_id}')
    # button_3 = InlineKeyboardButton(text='Задать вопрос', callback_data=f'question_ask_{question_id}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_2], [button_1]],)
    return keyboard


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


def keyboard_user_select_partner(tg_id: int, id_question: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора пользователя для диалога
    :return:
    """
    logging.info("keyboard_send")
    button_1 = InlineKeyboardButton(text=f'Выбрать',
                                    callback_data=f'selectpartner_{tg_id}_{id_question}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard


def keyboard_user_select_partner_gratis(tg_id: int, id_question: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора пользователя для диалога
    :return:
    """
    logging.info("keyboard_user_select_partner_gratis")
    button_1 = InlineKeyboardButton(text=f'Выбрать',
                                    callback_data=f'gratis_{tg_id}_{id_question}')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_1]])
    return keyboard

# def keyboard_user_question(question_id: int) -> InlineKeyboardMarkup:
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