from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f

import keyboards.user.keyboard_send_question as kb
import database.requests as rq
from database.models import User, Rate, Subscribe, Question
from utils.error_handling import error_handler

from config_data.config import Config, load_config

import logging
from datetime import datetime
import random
import asyncio

config: Config = load_config()
router = Router()


class QuestionState(StatesGroup):
    question = State()


@router.callback_query(F.data == 'send_question')
@error_handler
async def send_question(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Старт функционала задания вопроса
    :param callback:
    :param bot:
    :param state:
    :return:
    """
    logging.info('send_question')
    # проверка на наличие активной подписки
    subscribes: list[Subscribe] = await rq.get_subscribes_user(tg_id=callback.from_user.id)
    active_subscribe = False
    if subscribes:
        last_subscribe: Subscribe = subscribes[-1]
        date_format = '%d-%m-%Y %H:%M'
        current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        delta_time = (datetime.strptime(current_date, date_format) -
                      datetime.strptime(last_subscribe.date_completion, date_format))
        rate: Rate = await rq.get_rate_id(rate_id=last_subscribe.rate_id)
        if delta_time.days < rate.duration_rate:
            active_subscribe = True
    if not subscribes or not active_subscribe:
        await callback.message.answer(text=f'Действие вашей подписки завершено, продлите подписку')
    else:
        await callback.message.answer(text='Пришлите описание вашей проблемы, можете добавить фото 📎 .')
        await state.set_state(QuestionState.question)
        await state.update_data(content=[])
        await state.update_data(count=[])
        await state.update_data(task='')
    await callback.answer()


@router.message(StateFilter(QuestionState.question), or_f(F.photo, F.text))
@error_handler
async def request_content_photo_text(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем от пользователя контент для публикации
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'request_content_photo_text {message.chat.id}')
    await asyncio.sleep(random.random())
    data = await state.get_data()
    list_content = data.get('content', [])
    count = data.get('count', [])

    if message.text:
        data = await state.get_data()
        if data['task'] == '':
            task = data['task'] + '\n' + message.html_text
        else:
            task = message.html_text
        await state.update_data(task=task)
        await message.answer(text=f'📎 Прикрепите фото (можно несколько)\n'
                                  f'Добавить еще материал или отправить?',
                             reply_markup=kb.keyboard_send())

    elif message.photo:
        content = message.photo[-1].file_id
        list_content.append(content)
        count.append(content)
    await state.update_data(content=list_content)
    await state.update_data(count=count)
    await state.set_state(state=None)
    if len(count) == 1:
        await message.answer(text='Добавить еще материал или отправить?',
                             reply_markup=kb.keyboard_send())


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
    photos_id_list: list = question.photos_id.split(',')
    # формируем пост для рассылки
    if question.photos_id == '':
        msg = await bot.send_message(chat_id=partner.tg_id,
                                     text=text + '\n\n' + question.description,
                                     reply_markup=kb.keyboard_partner_question(question_id=id_question))
    elif len(photos_id_list) == 1:
        msg = await bot.send_photo(chat_id=partner.tg_id,
                                   photo=photos_id_list[0],
                                   caption=text + '\n\n' + question.description,
                                   reply_markup=kb.keyboard_partner_question(question_id=id_question))
    else:
        # собираем фото в медиа-группу
        media_group = []
        for photo_id in photos_id_list[:-1]:
            media_group.append(InputMediaPhoto(media=photo_id))
        # отправляем медиа-группу
        await bot.send_media_group(chat_id=partner.tg_id, media=media_group)
        msg = await bot.send_photo(chat_id=partner.tg_id,
                                   photo=photos_id_list[-1],
                                   caption=text + '\n\n' + question.description,
                                   reply_markup=kb.keyboard_partner_question(question_id=id_question))
    return msg


async def mailing_list_partner(callback: CallbackQuery, list_partner: list, question_id: int, bot: Bot):
    """
    Запуск рассылки по партнерам
    :param callback:
    :param list_partner:
    :param question_id:
    :param bot:
    :return:
    """
    if list_partner:
        for partner in list_partner:
            # получаем информацию о вопросе
            question: Question = await rq.get_question_id(question_id=question_id)
            list_partner_question = question.partner_list.split(',')
            if str(partner) in list_partner_question:
                continue
            text_1 = f"Поступил вопрос № {question_id} от пользователя <a href='tg://user?id={callback.from_user.id}'>" \
                     f"{callback.from_user.full_name}</a>"
            # добавляем партнера в список рассылки вопроса
            await rq.set_question_partner(question_id=question_id, partner_tg_id=partner.tg_id)

            msg_1 = await create_post_content(question=question, partner=partner, id_question=question_id, text=text_1,
                                              bot=bot)

            # запускаем таймер на 3 минуты
            await asyncio.sleep(60 * 3)
            # получаем информацию о вопросе
            question: Question = await rq.get_question_id(question_id=question_id)
            # если вопрос не находится в работе или не завершен, то предлагаем повторно взять заказ
            if question.status != rq.QuestionStatus.work or question.status != rq.QuestionStatus.completed:
                await bot.delete_message(chat_id=partner.tg_id,
                                         message_id=msg_1.message_id)
                text_2 = f"Напоминаю, что вопрос № {question_id} поступил от пользователя" \
                         f" <a href='tg://user?id={callback.from_user.id}'>" \
                         f"{callback.from_user.full_name}</a>"
                msg_2 = await create_post_content(question=question, partner=partner, id_question=question_id,
                                                  text=text_2,
                                                  bot=bot)

                # запускаем таймер на 3 минуты
                await asyncio.sleep(60 * 3)
                # получаем информацию о вопросе
                question: Question = await rq.get_question_id(question_id=question_id)
                # если вопрос не находится в работе или не завершен, то предлагаем повторно взять заказ
                if question.status != rq.QuestionStatus.work or question.status != rq.QuestionStatus.completed:
                    await bot.delete_message(chat_id=partner.tg_id,
                                             message_id=msg_2.message_id)
                    text_3 = f"Последняя возможность взять вопрос № {question_id} поступивший от пользователя" \
                             f" <a href='tg://user?id={callback.from_user.id}'>" \
                             f"{callback.from_user.full_name}</a>"
                    msg_3 = await create_post_content(question=question, partner=partner, id_question=question_id,
                                                      text=text_3,
                                                      bot=bot)

                    # запускаем таймер на 3 минуты
                    await asyncio.sleep(60 * 3)
                    # получаем информацию о вопросе
                    question: Question = await rq.get_question_id(question_id=question_id)
                    # если вопрос не находится в работе или не завершен, то предлагаем повторно взять заказ
                    if question.status != rq.QuestionStatus.work or question.status != rq.QuestionStatus.completed:
                        await bot.delete_message(chat_id=partner.tg_id,
                                                 message_id=msg_3.message_id)
                    else:
                        break
                else:
                    break
            else:
                break


@router.callback_query(F.data.endswith('content'))
@error_handler
async def send_add_content(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Добавления контента к вопросу или его отправка
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'send_add_content {callback.message.chat.id}')
    answer = callback.data.split('_')[0]

    if answer == 'add':
        await state.set_state(QuestionState.question)
        await state.update_data(count=[])
        await callback.message.edit_text(text='Пришлите описание вашей проблемы, можете добавить фото 📎 .')
    else:
        await callback.message.edit_text(text='Материалы от вас переданы\n\n',
                                         reply_markup=None)
        await rq.set_subscribe_user(tg_id=callback.from_user.id)
        data = await state.get_data()
        photos_id = ','.join(data['content'])
        data_question = {"tg_id": callback.from_user.id,
                         "description": data['task'],
                         "photos_id": photos_id,
                         "status": rq.QuestionStatus.create}
        id_question: int = await rq.add_question(data=data_question)
        list_partner: list[User] = await rq.get_users_role(role=rq.UserRole.partner)
        await mailing_list_partner(callback=callback, list_partner=list_partner, question_id=id_question, bot=bot)
    await callback.answer()
