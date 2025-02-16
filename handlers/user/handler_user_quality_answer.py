from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f

import keyboards.user.keyboard_user_quality_answer as kb
import database.requests as rq
from database.models import User, Rate, Subscribe, Question, Executor, Dialog
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


async def create_post_content(question: Question, partner: User, id_question: int, text: str, bot: Bot):
    """
    Функция для формирования поста с вопросом в зависимости от полученного контента
    :param question:
    :param partner:
    :param id_question:
    :param text:
    :param bot:
    :return:
    """
    logging.info('create_post_content')
    content_id: str = question.content_ids
    # формируем пост для рассылки
    if question.content_ids == '':
        await bot.send_message(chat_id=partner.tg_id,
                               text=question.description)
    else:
        typy_file = content_id.split('!')[0]
        if typy_file == 'photo':
            await bot.send_photo(chat_id=partner.tg_id,
                                 photo=content_id.split('!')[1],
                                 caption=question.description)
        elif typy_file == 'file':
            await bot.send_document(chat_id=partner.tg_id,
                                    document=content_id.split('!')[1],
                                    caption=question.description)
    msg = await bot.send_message(chat_id=partner.tg_id,
                                 text=text,
                                 reply_markup=kb.keyboard_partner_begin_question(question_id=id_question))
    return msg


async def mailing_list_partner(list_partner: list, question_id: int, bot: Bot):
    """
    Запуск рассылки по партнерам
    :param list_partner:
    :param question_id:
    :param bot:
    :return:
    """
    logging.info('mailing_list_partner')
    if list_partner:
        for partner in list_partner:
            info_dialog: Dialog = await rq.get_dialog_active_tg_id(tg_id=partner.tg_id)
            info_executor: Executor = await rq.get_executor(question_id=question_id, tg_id=partner.tg_id)
            if info_dialog or (info_executor and info_executor.status == rq.ExecutorStatus.cancel):
                continue
                # получаем информацию о вопросе
            question: Question = await rq.get_question_id(question_id=question_id)
            user: User = await rq.get_user_by_id(tg_id=question.tg_id)
            text_1 = f"Поступил вопрос № {question_id} от пользователя #_{user.id}.\n" \
                     f"Вы можете предложить стоимость решения вопроса," \
                     f" отказаться от его решения или уточнить детали у заказчика"
            msg_1 = await create_post_content(question=question, partner=partner, id_question=question_id, text=text_1,
                                              bot=bot)
            data_executor = {"tg_id": partner.tg_id,
                             "message_id": msg_1.message_id,
                             "id_question": question_id,
                             "cost": 0,
                             "status": rq.QuestionStatus.create}
            await rq.add_executor(data=data_executor)


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
        info_executor: Executor = await rq.get_executor(question_id=question_id,
                                                        tg_id=question.partner_solution)
        change_balance = info_executor.cost
        await rq.update_user_balance(tg_id=info_executor.tg_id,
                                     change_balance=change_balance)
        await rq.set_status_executor(question_id=question_id,
                                     tg_id=info_executor.tg_id,
                                     status=rq.QuestionStatus.completed)
        await rq.set_question_status(question_id=question_id,
                                     status=rq.QuestionStatus.completed)
    elif quality > 0:
        await callback.message.edit_text(text='Благодарим за обратную связь, нам очень важна ваша оценка!\n'
                                              'Укажите почему вы снизили оценку?',
                                         reply_markup=kb.keyboard_pass_comment())
        current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        await rq.set_question_data_solution(question_id=question_id, data_solution=current_date)
        await state.update_data(quality=quality)
        await state.set_state(StageQuality.state_comment)
        info_executor: Executor = await rq.get_executor(question_id=question_id,
                                                        tg_id=question.partner_solution)
        change_balance = info_executor.cost
        await rq.update_user_balance(tg_id=info_executor.tg_id,
                                     change_balance=change_balance)
        await rq.set_status_executor(question_id=question_id,
                                     tg_id=info_executor.tg_id,
                                     status=rq.QuestionStatus.completed)
        await rq.set_question_status(question_id=question_id,
                                     status=rq.QuestionStatus.completed)
    else:
        info_executor: Executor = await rq.get_executor(question_id=question_id,
                                                        tg_id=question.partner_solution)
        await callback.message.edit_text(text=f'Благодарим за обратную связь, постараемся решить вашу проблему!\n'
                                              f'Сумма в размере {info_executor.cost} рублей возвращена вам на баланс.\n'
                                              f'Вопрос снова разослан специалистам.\n'
                                              f'Диалог между вами и клиентом закрыт',
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
        info_executor: Executor = await rq.get_executor(question_id=question_id,
                                                        tg_id=partner.tg_id)
        change_balance = info_executor.cost
        await rq.update_user_balance(tg_id=callback.from_user.id,
                                     change_balance=change_balance)
        await rq.set_status_executor(question_id=question_id,
                                     tg_id=info_executor.tg_id,
                                     status=rq.QuestionStatus.cancel)
        await rq.set_question_executor(question_id=question_id,
                                       executor=0)
        list_partner: list[User] = await rq.get_users_role(role=rq.UserRole.partner)
        await mailing_list_partner(list_partner=list_partner,
                                   question_id=question_id,
                                   bot=bot)
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
