from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import Question
import logging


def keyboards_select_questions_delete(question: Question, count: int) -> InlineKeyboardMarkup:
    """
    Клавиатура с пагинацией для выбора вопроса
    :param question:
    :param count:
    :return:
    """
    logging.info(f'keyboards_add_partner')
    kb_builder = InlineKeyboardBuilder()
    buttons_cancel = InlineKeyboardButton(text='Удалить вопрос', callback_data=f'question_delete_{question.id}')
    button_back = InlineKeyboardButton(text='<<<<',
                                       callback_data=f'questions_back_{str(count)}')
    button_next = InlineKeyboardButton(text='>>>>',
                                       callback_data=f'questions_forward_{str(count)}')

    kb_builder.row(buttons_cancel, width=1)
    kb_builder.row(button_back, button_next)

    return kb_builder.as_markup()
