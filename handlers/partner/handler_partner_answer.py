from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f

import keyboards.partner.keyboard_partner_answer as kb
import database.requests as rq
from database.models import User, Rate, Subscribe, Question
from utils.error_handling import error_handler
from handlers.user.handler_send_question import mailing_list_partner

from config_data.config import Config, load_config

import logging
from datetime import datetime
import random
import asyncio

config: Config = load_config()
router = Router()


@router.callback_query(F.data.startswith('question_'))
@error_handler
async def partner_answer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Старт функционала ответа на вопрос
    :param callback:
    :param bot:
    :param state:
    :return:
    """
    logging.info('send_question')
    answer: str = callback.data.split('_')[1]
    question_id: str = callback.data.split('_')[-1]
    if answer == 'attach':
        question: Question = await rq.get_question_id(question_id=int(question_id))
        user: User = await rq.get_user_by_id(tg_id=question.tg_id)
        await rq.set_question_status(question_id=int(question_id),
                                     status=rq.QuestionStatus.work)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(text=f"Вы взяли вопрос №{question.id} для ответа или уточнения деталей"
                                           f" напишите заказчику <a href='tg://user?id={question.tg_id}'>"
                                           f"{user.username}</a>",
                                      reply_markup=kb.keyboard_partner_reject(question_id=int(question_id)))
    elif answer == 'reject':
        question: Question = await rq.get_question_id(question_id=int(question_id))
        await rq.set_question_status(question_id=int(question_id),
                                     status=rq.QuestionStatus.cancel)
        await callback.message.edit_text(text=f"Вы отказались от вопроса №{question.id}",
                                         reply_markup=None)
        list_partner: list[User] = await rq.get_users_role(role=rq.UserRole.partner)
        await mailing_list_partner(callback=callback, list_partner=list_partner, question_id=int(question_id), bot=bot)
    elif answer == 'completed':
        question: Question = await rq.get_question_id(question_id=int(question_id))
        await rq.set_question_status(question_id=int(question_id),
                                     status=rq.QuestionStatus.completed)
        await rq.set_question_completed(question_id=int(question_id), partner=callback.from_user.id)
        await callback.message.edit_text(text=f"Вы выполнили заказ №{question.id} и он занесен в БД",
                                         reply_markup=None)
        await bot.send_message(chat_id=question.tg_id,
                               text='Пожалуйста оцените качество решения ваше проблемы!',
                               reply_markup=kb.keyboard_quality_answer(question_id=int(question_id)))
    await callback.answer()

