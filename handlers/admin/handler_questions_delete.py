from aiogram.types import CallbackQuery, Message
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from keyboards.admin import keyboards_questions_delete as kb
from filter.admin_filter import IsSuperAdmin
from database import requests as rq
from database.models import Question, Executor, User
from utils.error_handling import error_handler
import logging
from datetime import datetime, timedelta

router = Router()


class StateAccount(StatesGroup):
    fullname = State()
    withdrawal_funds = State()


async def create_post_content(question: Question, partner: User, count: int, text: str, bot: Bot):
    """
    Функция для формирования поста с вопросом в зависимости от полученного контента
    :param question:
    :param partner:
    :param count:
    :param text:
    :param bot:
    :return:
    """
    logging.info('create_post_content')
    content_id: str = question.content_ids
    # формируем пост для рассылки
    if question.content_ids == '':
        msg = await bot.send_message(chat_id=partner.tg_id,
                                     text=f'{text}\n\n{question.description}',
                                     reply_markup=kb.keyboards_select_questions_delete(question=question,
                                                                                       count=count))
    else:
        typy_file = content_id.split('!')[0]
        if typy_file == 'photo':
            msg = await bot.send_photo(chat_id=partner.tg_id,
                                       photo=content_id.split('!')[1],
                                       caption=f'{text}\n\n{question.description}',
                                       reply_markup=kb.keyboards_select_questions_delete(question=question,
                                                                                         count=count))
        elif typy_file == 'file':
            msg = await bot.send_document(chat_id=partner.tg_id,
                                          document=content_id.split('!')[1],
                                          caption=f'{text}\n\n{question.description}',
                                          reply_markup=kb.keyboards_select_questions_delete(question=question,
                                                                                            count=count))


@router.message(F.text == 'Вопросы', IsSuperAdmin())
@error_handler
async def process_buttons_questions(message: Message, state: FSMContext, bot: Bot):
    """
    Личный кабинет партнера
    :param message:
    :param state:
    :param bot
    :return:
    """
    logging.info('process_buttons_questions')
    list_question: list[Question] = await rq.get_questions_cancel_create()
    if list_question:
        user_info: User = await rq.get_user_by_id(list_question[0].tg_id)
        partner_info: User = await rq.get_user_by_id(tg_id=message.from_user.id)
        preview_text = f"Вопрос № {list_question[0].id} от пользователя #_{user_info.id}.\n" \
                       f"Вы можете предложить стоимость решения вопроса," \
                       f" отказаться от его решения"
        await create_post_content(question=list_question[0],
                                  partner=partner_info,
                                  count=0,
                                  text=preview_text,
                                  bot=bot)
    else:
        await message.answer(text='Вопросов для отображения НЕТ')

@router.callback_query(F.data.startswith('questions_back_'))
@router.callback_query(F.data.startswith('questions_forward_'))
@error_handler
async def back_forward_list_questions(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Пагинация по списку вопросов
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('back_forward_list_questions')
    await callback.message.delete()
    count = int(callback.data.split('_')[-1])
    new_count = count - 1
    if callback.data.startswith('questions_forward_'):
        new_count = count + 1
    list_question: list[Question] = await rq.get_questions_cancel_create()
    if len(list_question) == new_count:
        new_count = 0
    elif new_count < 0:
        new_count = len(list_question) - 1
    question: Question = list_question[new_count]
    user_info: User = await rq.get_user_by_id(question.tg_id)
    partner_info: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
    preview_text = f"Вопрос № {question.id} от пользователя #_{user_info.id}.\n" \
                   f"Вы можете предложить стоимость решения вопроса," \
                   f" отказаться от его решения"
    await create_post_content(question=question,
                              partner=partner_info,
                              count=new_count,
                              text=preview_text,
                              bot=bot)
    await callback.answer()



