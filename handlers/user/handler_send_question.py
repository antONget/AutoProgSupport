from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f

import keyboards.user.keyboard_send_question as kb
from keyboards.user.keyboards_rate import keyboards_select_rate
import database.requests as rq
from database.models import User, Rate, Subscribe, Question, Dialog
from utils.error_handling import error_handler

from config_data.config import Config, load_config

import logging
from datetime import datetime
import random
import asyncio

config: Config = load_config()
router = Router()
router.message.filter(F.chat.type == "private")


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
    info_dialog: Dialog = await rq.get_dialog_active_tg_id(tg_id=callback.from_user.id)
    if info_dialog:
        await callback.message.edit_text(text='В данный момент у вас есть один не закрытый диалог для его закрытия введите команду'
                                              ' /close_dialog',
                                         reply_markup=None)
        await callback.answer()
        return
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
            rate: Rate = await rq.get_rate_id(rate_id=last_subscribe.rate_id)
            if last_subscribe.count_question < rate.question_rate:
                active_subscribe = True
    if not subscribes or not active_subscribe:
        list_rates: list[Rate] = await rq.get_list_rate()
        await callback.message.edit_text(text=f'Действие вашей подписки завершено, продлите подписку',
                                         reply_markup=keyboards_select_rate(list_rate=list_rates))
    else:
        await callback.message.edit_text(text='Пришлите описание вашей проблемы, можете добавить фото или файл 📎 .',
                                         reply_markup=None)
        await state.set_state(QuestionState.question)
        await state.update_data(content='')
        # await state.update_data(count=[])
        await state.update_data(task='')
    await callback.answer()


@router.message(StateFilter(QuestionState.question), or_f(F.photo, F.text, F.document))
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
    # await asyncio.sleep(random.random())
    # await state.update_data(content=[])
    # await state.update_data(count=[])
    # await state.update_data(task='')
    data = await state.get_data()
    # list_content = data.get('content', [])
    # count = data.get('count', [])
    content = data['content']
    task = data['task']
    if message.text:
        # data = await state.get_data()
        if task == '':
            task = message.html_text
        else:
            task += f'\n + {message.html_text}'
        await state.update_data(task=task)
        # await message.edit_text(text=f'📎 Прикрепите фото или файл.\n'
        #                              f'Добавить еще материал или отправить?',
        #                         reply_markup=kb.keyboard_send())

    elif message.photo:
        content = f'photo!{message.photo[-1].file_id}'
        task = data['task']
        if message.caption:
            if task == '':
                task = message.caption
            else:
                task += f'\n{message.caption}'
            await state.update_data(task=task)
        await state.update_data(content=content)
    elif message.document:
        logging.info(f'{message.document.file_id}')
        content = f'file!{message.document.file_id}'
        task = data['task']
        if message.caption:
            if task == '':
                task = message.caption
            else:
                task += f'\n{message.caption}'
            await state.update_data(task=task)
        await state.update_data(content=content)
    # await state.update_data(count=count)
    await state.set_state(state=None)
    if content == '':
        await message.answer(text=f'{task}\n\n'
                                  f'📎 Прикрепите фото или файл.\n'
                                  f'Добавить еще материал или отправить?',
                             reply_markup=kb.keyboard_send())
    else:
        typy_file = content.split('!')[0]
        if typy_file == 'photo':
            await message.answer_photo(photo=content.split('!')[1],
                                       caption=f'{task}\n\n'
                                               f'📎 Прикрепите фото или файл.\n'
                                               f'Добавить еще материал или отправить?',
                                       reply_markup=kb.keyboard_send())
        elif typy_file == 'file':
            await message.answer_document(document=content.split('!')[1],
                                          caption=f'{task}\n\n'
                                                  f'📎 Прикрепите фото или файл.\n'
                                                  f'Добавить еще материал или отправить?',
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
    content_id: str = question.content_ids
    # формируем пост для рассылки
    msg = 0
    if question.content_ids == '':
        msg = await bot.send_message(chat_id=partner.tg_id,
                                     text=question.description)
    else:
        typy_file = content_id.split('!')[0]
        if typy_file == 'photo':
            msg = await bot.send_photo(chat_id=partner.tg_id,
                                       photo=content_id.split('!')[1],
                                       caption=question.description)
        elif typy_file == 'file':
            msg = await bot.send_document(chat_id=partner.tg_id,
                                          document=content_id.split('!')[1],
                                          caption=question.description)
    msg = await bot.send_message(chat_id=partner.tg_id,
                                 text=text,
                                 reply_markup=kb.keyboard_partner_begin_question(question_id=id_question))
    # else:
    #     for file_id in content_id_list:
    #         typy_file = file_id.split('!')[0]
    #         if typy_file == 'photo':
    #             msg = await bot.send_photo(chat_id=partner.tg_id,
    #                                        photo=content_id_list[0],
    #                                        caption=text + '\n\n' + question.description,
    #                                        reply_markup=kb.keyboard_partner_question(question_id=id_question))
    #         elif typy_file == 'file':
    #             msg = await bot.send_document(chat_id=partner.tg_id,
    #                                           document=content_id_list[0],
    #                                           caption=text + '\n\n' + question.description,
    #                                           reply_markup=kb.keyboard_partner_question(question_id=id_question))
        # # собираем фото в медиа-группу
        # media_group = []
        # for photo_id in content_id_list[:-1]:
        #     media_group.append(InputMediaPhoto(media=photo_id))
        # # отправляем медиа-группу
        # await bot.send_media_group(chat_id=partner.tg_id, media=media_group)
        # msg = await bot.send_photo(chat_id=partner.tg_id,
        #                            photo=photos_id_list[-1],
        #                            caption=text + '\n\n' + question.description,
        #                            reply_markup=kb.keyboard_partner_question(question_id=id_question))
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
    logging.info('mailing_list_partner')
    if list_partner:
        for partner in list_partner:
            info_dialog: Dialog = await rq.get_dialog_active_tg_id(tg_id=partner.tg_id)
            if info_dialog:
                continue
                # получаем информацию о вопросе
            question: Question = await rq.get_question_id(question_id=question_id)
            user: User = await rq.get_user_by_id(tg_id=question.tg_id)
            # list_partner_question = question.partner_list.split(',')
            # if str(partner.tg_id) in list_partner_question:
            #     continue
            text_1 = f"Поступил вопрос № {question_id} от пользователя #_{user.id}.\n" \
                     f"Вы можете предложить стоимость решения вопроса," \
                     f" отказаться от его решения или уточнить детали у заказчика"
            msg_1 = await create_post_content(question=question, partner=partner, id_question=question_id, text=text_1,
                                              bot=bot)
            # добавляем партнера в список рассылки вопроса
            # await rq.set_question_partner(question_id=question_id,
            #                               partner_tg_id=partner.tg_id,
            #                               message_id=msg_1.message_id)
            data_executor = {"tg_id": partner.tg_id,
                             "message_id": msg_1.message_id,
                             "id_question": question_id,
                             "cost": 0,
                             "status": rq.QuestionStatus.create}
            await rq.add_executor(data=data_executor)
            # # запускаем таймер на 3 минуты
            # await asyncio.sleep(60 * 3)
            # # получаем информацию о вопросе
            # question: Question = await rq.get_question_id(question_id=question_id)
            # # если вопрос не находится в работе или не завершен, то предлагаем повторно взять заказ
            # if question.status == rq.QuestionStatus.create or question.status == rq.QuestionStatus.cancel:
            #     await bot.delete_message(chat_id=partner.tg_id,
            #                              message_id=msg_1.message_id)
            #     text_2 = f"Напоминаю, что вопрос № {question_id} поступил от пользователя" \
            #              f" <a href='tg://user?id={question.tg_id}'>" \
            #              f"{user.username}</a>"
            #     msg_2 = await create_post_content(question=question, partner=partner, id_question=question_id,
            #                                       text=text_2,
            #                                       bot=bot)
            #
            #     # запускаем таймер на 3 минуты
            #     await asyncio.sleep(60 * 3)
            #     # получаем информацию о вопросе
            #     question: Question = await rq.get_question_id(question_id=question_id)
            #     # если вопрос не находится в работе или не завершен, то предлагаем повторно взять заказ
            #     if question.status == rq.QuestionStatus.create or question.status == rq.QuestionStatus.cancel:
            #         await bot.delete_message(chat_id=partner.tg_id,
            #                                  message_id=msg_2.message_id)
            #         text_3 = f"Последняя возможность взять вопрос № {question_id} поступивший от пользователя" \
            #                  f" <a href='tg://user?id={question.tg_id}'>" \
            #                  f"{user.username}</a>"
            #         msg_3 = await create_post_content(question=question, partner=partner, id_question=question_id,
            #                                           text=text_3,
            #                                           bot=bot)
            #
            #         # запускаем таймер на 3 минуты
            #         await asyncio.sleep(60 * 3)
            #         # получаем информацию о вопросе
            #         question: Question = await rq.get_question_id(question_id=question_id)
            #         # если вопрос не находится в работе или не завершен, то предлагаем повторно взять заказ
            #         if question.status == rq.QuestionStatus.create or question.status == rq.QuestionStatus.cancel:
            #             await bot.delete_message(chat_id=partner.tg_id,
            #                                      message_id=msg_3.message_id)
            #         else:
            #             break
            #     else:
            #         break
            # else:
            #     break


@router.callback_query(F.data.endswith('content'))
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
    await callback.answer()
    if answer == 'add':
        await state.set_state(QuestionState.question)
        await state.update_data(count=[])
        await callback.message.delete()
        await callback.message.answer(text='Пришлите описание вашей проблемы, можете добавить фото 📎 .')
    else:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(text='Материалы от вас переданы\n\n'
                                           'Ожидайте ответа от специалистов о стоимости решения вашего вопроса',
                                      reply_markup=None)
        data = await state.get_data()
        data_question = {"tg_id": callback.from_user.id,
                         "description": data['task'],
                         "content_ids": data['content'],
                         "status": rq.QuestionStatus.create}
        id_question: int = await rq.add_question(data=data_question)
        list_partner: list[User] = await rq.get_users_role(role=rq.UserRole.partner)
        await mailing_list_partner(callback=callback, list_partner=list_partner, question_id=id_question, bot=bot)
