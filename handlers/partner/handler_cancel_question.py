from aiogram.types import Message
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from utils.error_handling import error_handler
from utils.send_admins import send_message_admins
from filter.user_filter import IsRolePartner
from database.models import User, Dialog, Question, Executor
from database import requests as rq
from keyboards.partner.keyboard_cancel_question import keyboard_start, keyboard_partner_begin_question

import logging
from config_data.config import Config, load_config

router = Router()

config: Config = load_config()


class StateCancelQuestion(StatesGroup):
    reason_cancel_question = State()


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
                                 reply_markup=keyboard_partner_begin_question(question_id=id_question))
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
            if info_dialog:
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


@router.message(F.text == 'Отказаться от вопроса', IsRolePartner())
@error_handler
async def press_reason_cancel_question(message: Message, state: FSMContext, bot: Bot):
    """
    Отказ от решения вопроса
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('press_reason_cancel_question')
    await state.set_state(state=None)
    await message.answer(text='Пришлите причину отказа от решения вопроса')
    await state.set_state(StateCancelQuestion.reason_cancel_question)


@router.message(F.text, StateFilter(StateCancelQuestion.reason_cancel_question))
@error_handler
async def get_reason_cancel_question(message: Message, state: FSMContext, bot: Bot):
    """
    Получение причины отказа от решения вопроса
    :param message:
    :param state:
    :param bot:
    :return:
    """
    reason_cancel = message.text
    info_dialog: Dialog = await rq.get_dialog_active_tg_id(tg_id=message.from_user.id)
    info_partner: User = await rq.get_user_by_id(tg_id=info_dialog.tg_id_partner)
    info_user: User = await rq.get_user_by_id(tg_id=info_dialog.tg_id_user)
    info_question: Question = await rq.get_question_id(question_id=info_dialog.id_question)
    info_executor: Executor = await rq.get_executor(question_id=info_question.id,
                                                    tg_id=message.from_user.id)
    # ПАРТНЕР
    await message.answer(text=f'Вы отказались от решения вопроса №{info_dialog.id}\n\n'
                              f'Вопрос снова разослан партнерам.\n'
                              f'Диалог между вами и клиентом закрыт',
                         reply_markup=keyboard_start(role=rq.UserRole.partner))
    await rq.set_executor_comment_cancel(question_id=info_dialog.id_question,
                                         tg_id=message.from_user.id,
                                         comment_cancel=reason_cancel)
    await rq.set_dialog_completed_tg_id(tg_id=message.from_user.id)
    await rq.set_question_executor(question_id=info_dialog.id_question,
                                   executor=0)
    await rq.set_question_status(question_id=info_dialog.id_question,
                                 status=rq.QuestionStatus.cancel)
    await rq.set_status_executor(question_id=info_dialog.id_question,
                                 tg_id=message.from_user.id,
                                 status=rq.QuestionStatus.cancel)

    # АДМИНИСТРАТОР
    if info_partner.fullname != "none":
        name_text = info_partner.fullname
    else:
        name_text = f"#_{info_partner.id}"
    await send_message_admins(bot=bot,
                              text=f'Партнер {name_text} отказался от решения вопроса №{info_question.id} по причине:'
                                   f' {reason_cancel}.\n\n'
                                   f'Вопрос запущен снова на рассылку партнерам')
    # ПОЛЬЗОВАТЕЛЬ
    if info_partner.fullname != "none":
        name_text = info_partner.fullname
    else:
        name_text = f"#_{info_partner.id}"
    await bot.send_message(chat_id=info_user.tg_id,
                           text=f'Специалист {name_text} отказался от решения вашего вопроса №{info_question.id}.\n'
                                f'Сумма в размере {info_executor.cost} рублей возвращена вам на баланс.\n'
                                f'Вопрос снова разослан специалистам.\n'
                                f'Диалог между вами и клиентом закрыт')
    await rq.update_user_balance(tg_id=info_user.tg_id,
                                 change_balance=info_executor.cost)

    list_partner: list[User] = await rq.get_users_role(role=rq.UserRole.partner)
    list_partner_not_cancel: list[User] = [partner for partner in list_partner if partner.tg_id != message.from_user.id]
    await mailing_list_partner(list_partner=list_partner_not_cancel,
                               question_id=info_question.id,
                               bot=bot)
