from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f

import database.requests as rq
from database.models import User, Rate, Subscribe, Question, Executor
from utils.error_handling import error_handler
from services.yookassa.payments import create_payment_yookassa, check_payment
from keyboards.user import keyboard_select_partner as kb
from config_data.config import Config, load_config

import logging
from datetime import datetime
import random
import asyncio

config: Config = load_config()
router = Router()


class StageSelectPartner(StatesGroup):
    dialog_partner = State()


@router.callback_query(F.data.startswith('selectpartner_'))
@error_handler
async def process_selectpartner(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Выбор партнера для работы с ним по решению вопроса
    :param callback: selectpartner_{tg_id}_{id_question}
    :param bot:
    :param state:
    :return:
    """
    logging.info('process_selectpartner')
    tg_id_partner: str = callback.data.split('_')[1]
    id_question: str = callback.data.split('_')[-1]
    info_partner: User = await rq.get_user_by_id(tg_id=int(tg_id_partner))
    info_user: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
    info_question: Question = await rq.get_question_id(question_id=int(id_question))
    info_executor: Executor = await rq.get_executor(question_id=int(id_question), tg_id=int(tg_id_partner))
    payment_url, payment_id = create_payment_yookassa(amount=info_executor.cost,
                                                      chat_id=callback.from_user.id,
                                                      content="Услуга по решению вопроса")
    await callback.message.edit_text(text=f'Специалист #_{info_partner.id} оценил стоимость решения'
                                          f' вопроса № {id_question} в {info_executor.cost} рублей. \n'
                                          f'Для выбора этого специалиста для решения вашего вопроса оплатите указанную'
                                          f' стоимость и после успешной оплаты нажмите "Продолжить"',
                                     reply_markup=kb.keyboard_payment_user_question(payment_url=payment_url,
                                                                                    payment_id=payment_id,
                                                                                    amount=info_executor.cost,
                                                                                    id_question=id_question))
    await bot.send_message(chat_id=tg_id_partner,
                           text=f'Вас выбрал пользователь #_{info_user.id} для решения вопроса {id_question}')
    executors: list[Executor] = await rq.get_executors(question_id=int(id_question))
    list_executors: list = [executor for executor in executors]
    for executor in list_executors:
        # try:
        await bot.delete_message(chat_id=executor.tg_id,
                                 message_id=executor.message_id)
        # except:
        #     pass
        try:
            await bot.delete_message(chat_id=callback.from_user.id,
                                     message_id=executor.message_id_cost)
        except:
            pass
        await rq.del_executor(question_id=int(id_question), tg_id=int(executor.tg_id))
    await rq.set_question_executor(question_id=int(id_question), executor=int(tg_id_partner))


@router.callback_query(F.data.startswith('payquestion_'))
async def check_pay_select_partner(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Проверка оплаты
    :param callback: payquestion_{id_question}_{payment_id}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'check_pay_select_partner {callback.message.chat.id}')
    payment_id: str = callback.data.split('_')[-1]
    id_question: str = callback.data.split('_')[-2]
    result = check_payment(payment_id=payment_id)
    # result = 'succeeded'
    if result == 'succeeded':
        await rq.set_subscribe_user(tg_id=callback.from_user.id)
        info_question: Question = await rq.get_question_id(question_id=int(id_question))
        await callback.message.delete()
        await callback.message.answer(text='Платеж прошел успешно',
                                      reply_markup=kb.keyboard_open_dialog_partner(id_question=id_question))
        await bot.send_message(chat_id=info_question.partner_solution,
                               text=f'Пользователь оплатил решение вопроса № {info_question.id}',
                               reply_markup=kb.keyboard_open_dialog_user(id_question=id_question))
        data_dialog = {"tg_id_user": callback.from_user.id,
                       "tg_id_partner": info_question.partner_solution,
                       "id_question": int(id_question)}
        await rq.add_dialog(data=data_dialog)
    else:
        await callback.answer(text='Платеж не прошел', show_alert=True)


@router.callback_query(F.data.startswith('open_dialog_partner_'))
async def open_dialog_partner(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Проверка оплаты
    :param callback: open_dialog_partner_{id_question}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'open_dialog_partner {callback.message.chat.id}')
    id_question: str = callback.data.split('_')[-1]
    info_question: Question = await rq.get_question_id(question_id=int(id_question))
    await state.update_data(partner_dialog=info_question.partner_solution)
    await state.update_data(id_question=id_question)
    await state.set_state(StageSelectPartner.dialog_partner)
    info_partner: User = await rq.get_user_by_id(tg_id=info_question.partner_solution)
    await callback.message.answer(text=f'Вы открыли диалог со специалистом #_{info_partner.id},'
                                       f' все ваши сообщения будут перенаправлены ему,'
                                       f' для завершения диалога нажмите "Завершить диалог"',
                                  reply_markup=kb.keyboard_finish_dialog())
    await callback.answer()


@router.message(StateFilter(StageSelectPartner.dialog_partner), F.text == 'Завершить диалог')
@error_handler
async def finish_dialog_user(message: Message, state: FSMContext, bot: Bot):
    """
    Завершение диалога с партнером пользователем
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'finish_dialog_user {message.chat.id}')
    await state.set_state(state=None)
    data = await state.get_data()
    partner_dialog: int = data['partner_dialog']
    id_question: str = data['id_question']
    info_partner: User = await rq.get_user_by_id(tg_id=partner_dialog)

    await message.answer(text=f'Диалог со специалистом #_{info_partner.id} для решения вопроса № {id_question} закрыт.'
                              f' Оцените качество решения вашего вопроса',
                         reply_markup=kb.keyboard_quality_answer(question_id=int(id_question)))


@router.message(StateFilter(StageSelectPartner.dialog_partner), or_f(F.photo, F.text, F.document, F.video))
@error_handler
async def request_content_photo_text(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем от пользователя контент и отправляем его партнеру
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'request_content_photo_text {message.chat.id}')
    data = await state.get_data()
    partner_dialog = data['partner_dialog']
    info_user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    autor = f'Получено сообщение от пользователя #_{info_user.id}, для ответа откройте диалог с эти пользователем'
    if message.text:
        await bot.send_message(chat_id=partner_dialog,
                               text=f'{autor}\n\n'
                                    f'{message.text}')
    elif message.photo:
        photo_id = message.photo[-1].file_id
        await bot.send_photo(chat_id=partner_dialog,
                             photo=photo_id,
                             caption=f'{autor}\n\n{message.caption}')
    elif message.document:
        document_id = message.document.file_id
        await bot.send_document(chat_id=partner_dialog,
                                document=document_id,
                                caption=f'{autor}\n\n{message.caption}')
    else:
        await message.answer(text='Такой контент отправить не могу, вы можете отправить: текст, фото или документ')


