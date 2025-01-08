from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f

import keyboards.user.keyboard_send_question as kb
import database.requests as rq
from database.models import User, Rate, Subscribe, Question
from utils.error_handling import error_handler
from utils.send_admins import send_message_admins

from config_data.config import Config, load_config

import logging
from datetime import datetime
import random
import asyncio

config: Config = load_config()
router = Router()


@router.callback_query(F.data.startswith('quality_'))
@error_handler
async def quality_answer_question(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Качество ответа на вопрос
    :param callback:
    :param bot:
    :param state:
    :return:
    """
    logging.info('quality_answer_question')
    question_id = int(callback.data.split('_')[-1])
    quality = int(callback.data.split('_')[1])
    await rq.set_question_quality(question_id=question_id, quality=quality)
    question: Question = await rq.get_question_id(question_id=question_id)
    user: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
    if quality:
        await callback.message.edit_text(text='Благодарим за обратную связь, нам очень важна ваша оценка!',
                                         reply_markup=None)
        text_quality = '⭐' * quality
        await bot.send_message(chat_id=question.partner_solution,
                               text=f"Пользователь <a href='tg://user?id={question.tg_id}'>{user.username}</a>"
                                    f"оценил вашу помощь на вопрос №{question.id} на {text_quality}")
    else:
        await callback.message.edit_text(text='Благодарим за обратную связь, постараемся решить вашу проблему!',
                                         reply_markup=None)
        await bot.send_message(chat_id=question.partner_solution,
                               text=f"Пользователь <a href='tg://user?id={question.tg_id}'>{user.username}</a> "
                                    f"указал, что вопрос №{question.id} не решен")
        partner: User = await rq.get_user_by_id(tg_id=question.partner_solution)
        await send_message_admins(bot=bot, text=f"Пользователь "
                                                f"<a href='tg://user?id={question.tg_id}'>{user.username}</a>"
                                                f"указал, что вопрос №{question.id} не решен партнером "
                                                f"<a href='tg://user?id={question.partner_solution}'>"
                                                f"{partner.username}</a>")
    await callback.answer()

