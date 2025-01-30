from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f

import keyboards.partner.keyboard_partner_answer as kb
import database.requests as rq
from database.models import User, Rate, Subscribe, Question, Executor
from utils.error_handling import error_handler
from config_data.config import Config, load_config

import logging


config: Config = load_config()
router = Router()


class StatePartner(StatesGroup):
    state_cost = State()
    state_ask = State()


@router.callback_query(F.data.startswith('question_'))
@error_handler
async def partner_answer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Старт функционала работы над вопросом
    :param callback:
    :param bot:
    :param state:
    :return:
    """
    logging.info('send_question')
    answer: str = callback.data.split('_')[1]
    question_id: str = callback.data.split('_')[-1]
    await state.update_data(question_id=question_id)
    if answer == 'cost':
        question: Question = await rq.get_question_id(question_id=int(question_id))
        user: User = await rq.get_user_by_id(tg_id=question.tg_id)
        await callback.message.edit_text(text=f"Укажите стоимость решения вопроса №{question.id}")
        await state.set_state(StatePartner.state_cost)
    elif answer == 'reject':
        question: Question = await rq.get_question_id(question_id=int(question_id))
        await callback.message.edit_text(text=f"Вы отказались от вопроса №{question.id}",
                                         reply_markup=None)
        # list_partner: list[User] = await rq.get_users_role(role=rq.UserRole.partner)
        # await mailing_list_partner(callback=callback, list_partner=list_partner, question_id=int(question_id), bot=bot)
    elif answer == 'ask':
        question: Question = await rq.get_question_id(question_id=int(question_id))
        await callback.message.answer(text=f'Пришлите, что вы хотите уточнить по вопросу № {question_id} у пользователя'
                                           f' #_{question.tg_id}')
        # await rq.set_question_status(question_id=int(question_id),
        #                              status=rq.QuestionStatus.completed)
        # await rq.set_question_completed(question_id=int(question_id), partner=callback.from_user.id)
        # await callback.message.edit_text(text=f"Вы выполнили заказ №{question.id} и он занесен в БД",
        #                                  reply_markup=None)
        # await bot.send_message(chat_id=question.tg_id,
        #                        text='Пожалуйста оцените качество решения ваше проблемы!',
        #                        reply_markup=kb.keyboard_quality_answer(question_id=int(question_id)))
    await callback.answer()


@router.message(F.text, StateFilter(StatePartner.state_cost))
@error_handler
async def get_cost_question_partner(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем стоимость решения вопроса для отправки пользолвателю
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_cost_question_partner')
    cost = message.text
    data = await state.get_data()
    question_id = data['question_id']
    await message.delete()
    if cost.isdigit():
        try:
            await bot.delete_message(chat_id=message.from_user.id,
                                     message_id=message.message_id - 1)
        except:
            pass
        msg_1 = await message.answer(text=f'Стоимость {message.text} для решения вопроса № {question_id}'
                                          f' передана пользователю',
                                     reply_markup=kb.keyboard_partner_continue_question(question_id=question_id))
        info_question: Question = await rq.get_question_id(question_id=int(question_id))
        info_user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
        # payment_url, payment_id = create_payment_yookassa(amount=message.text,
        #                                                   chat_id=message.from_user.id,
        #                                                   content="Услуга по решению вопроса")
        msg_2 = await bot.send_message(chat_id=info_question.tg_id,
                                     text=f'Специалист #_{info_user.id} оценил стоимость решения'
                                          f' вопроса № {question_id} в {message.text} рублей. \n'
                                          f'Для выбора этого специалиста для решения вашего вопроса нажмите "Выбрать" '
                                          f'или ожидайте ответа от других специалистов',
                                     reply_markup=kb.keyboard_user_select_partner(tg_id=message.from_user.id,
                                                                            id_question=question_id))
        info_executor: Executor = await rq.get_executor(question_id=int(question_id),
                                                        tg_id=message.from_user.id)
        if info_executor.message_id_cost:
            try:
                await bot.delete_message(chat_id=info_question.tg_id,
                                         message_id=info_executor.message_id_cost)
            except:
                pass
                               # reply_markup=kb.keyboard_payment_user_question(payment_url=payment_url,
                               #                                                payment_id=payment_id,
                               #                                                amount=cost,
                               #                                                id_question=question_id))
        await rq.set_cost_executor(question_id=question_id,
                                   tg_id=message.from_user.id,
                                   cost=int(cost))
        await rq.set_message_id_cost_executor(question_id=question_id,
                                              tg_id=message.from_user.id,
                                              message_id_cost=msg_2.message_id)
        await rq.set_message_id_executor(question_id=question_id,
                                         tg_id=message.from_user.id,
                                         message_id=msg_1.message_id)
        await state.set_state(state=None)
    else:
        await message.answer(text=f'Некорректные данные, повторите ввод')
