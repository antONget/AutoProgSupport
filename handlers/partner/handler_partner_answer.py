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
    Старт функционала работы над вопросом полученного от пользователя
    :param callback: question_cost_{question_id}, question_reject_{question_id}
    :param bot:
    :param state:
    :return:
    """
    logging.info('send_question')
    # получаем действие
    answer: str = callback.data.split('_')[1]
    # id вопроса над которым совершили действие
    question_id: str = callback.data.split('_')[-1]
    await state.update_data(question_id=question_id)
    # если действие "Указать стоимость"
    if answer == 'cost':
        # получаем информацию о вопросе по его id
        question: Question = await rq.get_question_id(question_id=int(question_id))
        user: User = await rq.get_user_by_id(tg_id=question.tg_id)
        await callback.message.edit_text(text=f"Укажите стоимость решения вопроса №{question.id}")
        await state.set_state(StatePartner.state_cost)
    # специалист нажал кнопку отказаться
    elif answer == 'reject':
        question: Question = await rq.get_question_id(question_id=int(question_id))
        executor: Executor = await rq.get_executor(question_id=question.id,
                                                   tg_id=callback.from_user.id)
        await rq.set_status_executor(question_id=int(question_id),
                                     tg_id=callback.from_user.id,
                                     status=rq.ExecutorStatus.cancel)
        await callback.message.edit_text(text=f"Вы отказались от вопроса №{question.id}",
                                         reply_markup=None)
        partner_info: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
        if executor.message_id_cost:
            if partner_info.fullname != "none":
                name_text = partner_info.fullname
            else:
                name_text = f"Специалист #_{partner_info.id}"
            await bot.edit_message_text(chat_id=question.tg_id,
                                        message_id=executor.message_id_cost,
                                        text=f'{name_text} отказался от решения вопроса'
                                             f' №{question.id}',
                                        reply_markup=None)
            # await bot.send_message(text=f'Специалист #_{partner_info.id} отказался от решения вопроса №{question.id}')
        else:
            if partner_info.fullname != "none":
                name_text = partner_info.fullname
            else:
                name_text = f"Специалист #_{partner_info.id}"
            await bot.send_message(chat_id=question.tg_id,
                                   text=f'{name_text} отказался от решения вопроса №{question.id}')
        # list_partner: list[User] = await rq.get_users_role(role=rq.UserRole.partner)
        # await mailing_list_partner(callback=callback, list_partner=list_partner, question_id=int(question_id), bot=bot)
    # elif answer == 'ask':
    #     question: Question = await rq.get_question_id(question_id=int(question_id))
    #     await callback.message.answer(text=f'Пришлите, что вы хотите уточнить по вопросу № {question_id} у пользователя'
    #                                        f' #_{question.tg_id}')
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
    Получаем стоимость решения вопроса для отправки пользователю
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
    if cost.isdigit() and int(cost) > 0:
        await rq.set_cost_executor(question_id=question_id,
                                   tg_id=message.from_user.id,
                                   cost=int(cost))
        try:
            await bot.delete_message(chat_id=message.from_user.id,
                                     message_id=message.message_id - 1)
        except:
            pass
        msg_1 = await message.answer(text=f'Стоимость {message.text} для решения вопроса № {question_id}'
                                          f' передана пользователю',
                                     reply_markup=kb.keyboard_partner_continue_question(question_id=question_id))
        info_question: Question = await rq.get_question_id(question_id=int(question_id))
        info_partner: User = await rq.get_user_by_id(tg_id=message.from_user.id)
        questions_list: list[Question] = await rq.get_questions_tg_id(partner_solution=message.from_user.id)
        if len(questions_list):
            reiting_partner: float = round(sum([question.quality for question in questions_list])/len(questions_list), 1)
        else:
            reiting_partner: str = '#'
        if info_partner.fullname != "none":
            name_text = info_partner.fullname
        else:
            name_text = f"Специалист #_{info_partner.id}"
        msg_2 = await bot.send_message(chat_id=info_question.tg_id,
                                       text=f'{name_text}\nРейтинг {reiting_partner}⭐\n'
                                            f' оценил стоимость решения'
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
        await rq.set_message_id_cost_executor(question_id=question_id,
                                              tg_id=message.from_user.id,
                                              message_id_cost=msg_2.message_id)
        await rq.set_message_id_executor(question_id=question_id,
                                         tg_id=message.from_user.id,
                                         message_id=msg_1.message_id)
        await state.set_state(state=None)
    elif cost.isdigit() and int(cost) == 0:
        try:
            await bot.delete_message(chat_id=message.from_user.id,
                                     message_id=message.message_id - 1)
        except:
            pass
        info_question: Question = await rq.get_question_id(question_id=int(question_id))
        info_user: User = await rq.get_user_by_id(tg_id=info_question.tg_id)
        msg_1 = await message.answer(text=f'Ваше предложение о решении вопроса № {question_id}'
                                          f' <b>бесплатно</b> передано пользователю #_{info_user.id}',
                                     reply_markup=kb.keyboard_partner_continue_question(question_id=question_id))
        info_partner: User = await rq.get_user_by_id(tg_id=message.from_user.id)
        if info_partner.fullname != "none":
            name_text = info_partner.fullname
        else:
            name_text = f"Специалист #_{info_partner.id}"
        msg_2 = await bot.send_message(chat_id=info_question.tg_id,
                                       text=f'{name_text} предлагает решить вопрос  № {question_id}'
                                            f' <b>бесплатно</b>. Для выбора этого специалиста для решения вашего вопроса'
                                            f' нажмите "Выбрать"',
                                       reply_markup=kb.keyboard_user_select_partner_gratis(tg_id=message.from_user.id,
                                                                                           id_question=question_id))
        info_executor: Executor = await rq.get_executor(question_id=int(question_id),
                                                        tg_id=message.from_user.id)
        if info_executor.message_id_cost:
            try:
                await bot.delete_message(chat_id=info_question.tg_id,
                                         message_id=info_executor.message_id_cost)
            except:
                pass
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
