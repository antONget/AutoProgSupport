from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f

import keyboards.user.keyboard_user_quality_answer as kb
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
router.message.filter(F.chat.type == "private")


class StageQuality(StatesGroup):
    state_comment = State()


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
    await state.update_data(id_question=question_id)
    quality = int(callback.data.split('_')[1])
    await rq.set_question_quality(question_id=question_id, quality=quality)
    question: Question = await rq.get_question_id(question_id=question_id)
    info_user: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
    if quality == 5:
        await callback.message.edit_text(text='Благодарим за обратную связь, нам очень важна ваша оценка!',
                                         reply_markup=None)
        text_quality = '⭐' * quality
        await bot.send_message(chat_id=question.partner_solution,
                               text=f"Пользователь #_{info_user.id} оценил вашу помощь на вопрос"
                                    f" № {question.id} на {text_quality}")
        current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        await rq.set_question_data_solution(question_id=question_id, data_solution=current_date)
    elif quality > 0:
        await callback.message.edit_text(text='Благодарим за обратную связь, нам очень важна ваша оценка!\n'
                                              'Укажите почему вы снизили оценку?',
                                         reply_markup=kb.keyboard_pass_comment())
        current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        await rq.set_question_data_solution(question_id=question_id, data_solution=current_date)
        await state.update_data(quality=quality)
        await state.set_state(StageQuality.state_comment)
    else:
        await callback.message.edit_text(text='Благодарим за обратную связь, постараемся решить вашу проблему!',
                                         reply_markup=None)
        await bot.send_message(chat_id=question.partner_solution,
                               text=f"Пользователь #_{info_user.id} "
                                    f"указал, что вопрос №{question.id} не решен")
        partner: User = await rq.get_user_by_id(tg_id=question.partner_solution)
        await send_message_admins(bot=bot, text=f"Пользователь "
                                                f"<a href='tg://user?id={question.tg_id}'>{info_user.username}</a>"
                                                f" указал, что вопрос №{question.id} не решен партнером "
                                                f"<a href='tg://user?id={question.partner_solution}'>"
                                                f"{partner.username}</a>")
    await callback.answer()


@router.message(StateFilter(StageQuality.state_comment), F.text)
@error_handler
async def get_comment_user(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем комментарий к решению вопроса от пользователя
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_comment_user')
    data = await state.get_data()
    id_question = data['id_question']
    quality = data['quality']
    await rq.set_question_comment(question_id=int(id_question), comment=message.text)
    text_quality = '⭐' * quality
    info_question: Question = await rq.get_question_id(question_id=int(id_question))
    info_user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    info_partner: User = await rq.get_user_by_id(tg_id=info_question.partner_solution)
    await bot.send_message(chat_id=info_question.partner_solution,
                           text=f"Пользователь #_{info_user.id} "
                                f"оценил вашу помощь на вопрос № {info_question.id} на {text_quality}.\n"
                                f"<i>Комментарий</i>: {message.text}")
    await message.answer(text='Ваша оценка и комментарий передана специалисту, спасибо!')
    print(quality)
    if quality < 4:
        await send_message_admins(bot=bot,
                                  text=f"Пользователь "
                                       f"<a href='tg://user?id={info_user.tg_id}'>{info_user.username}</a>"
                                       f" указал, что вопрос №{id_question} решен на {text_quality} партнером "
                                       f"<a href='tg://user?id={info_question.partner_solution}'>"
                                       f"{info_partner.username}</a>\n"
                                       f"<i>Комментарий</i>: {message.text}")
    await state.set_state(state=None)


@router.callback_query(F.data == "pass_comment")
@error_handler
async def pass_comment(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Пропускаем добавление комментария
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('pass_comment')
    data = await state.get_data()
    id_question = data['id_question']
    quality = data['quality']
    text_quality = '⭐' * quality
    info_question: Question = await rq.get_question_id(question_id=int(id_question))
    info_user: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
    info_partner: User = await rq.get_user_by_id(tg_id=info_question.partner_solution)
    await bot.send_message(chat_id=info_question.partner_solution,
                           text=f"Пользователь #_{info_user.id} "
                                f"оценил вашу помощь на вопрос № {info_question.id} на {text_quality}.\n"
                                f"<i>Комментарий</i>: отсутствует")
    await callback.message.edit_text(text='Ваша оценка передана специалисту, спасибо!',
                                     reply_markup=None)
    if quality < 4:
        await send_message_admins(bot=bot,
                                  text=f"Пользователь "
                                       f"<a href='tg://user?id={info_user.tg_id}'>{info_user.username}</a>"
                                       f" указал, что вопрос №{id_question} решен на {text_quality} партнером "
                                       f"<a href='tg://user?id={info_question.partner_solution}'>"
                                       f"{info_partner.username}</a>\n"
                                       f"<i>Комментарий</i>: отсутствует")
    await state.set_state(state=None)
