from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, FSInputFile
from aiogram.fsm.context import FSMContext, StorageKey
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f
from aiogram.types.forum_topic import ForumTopic

import database.requests as rq
from database.models import User, Rate, Subscribe, Question, Executor, Dialog
from utils.error_handling import error_handler
from services.yoomany.quickpay import yoomany_payment, yoomany_chek_payment

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
    logging.info(f'process_selectpartner {callback.data}')
    tg_id_partner: str = callback.data.split('_')[1]
    id_question: str = callback.data.split('_')[-1]
    await rq.set_question_executor(question_id=int(id_question), executor=int(tg_id_partner))
    info_partner: User = await rq.get_user_by_id(tg_id=int(tg_id_partner))
    info_user: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
    info_question: Question = await rq.get_question_id(question_id=int(id_question))
    info_executor: Executor = await rq.get_executor(question_id=int(id_question),
                                                    tg_id=int(tg_id_partner))

    if info_user.balance < info_executor.cost:
        quickpay_base_url, quickpay_redirected_url, payment_id = await yoomany_payment(amount=info_executor.cost)
        if info_partner.fullname != "none":
            name_text = info_partner.fullname
        else:
            name_text = f"Специалист #_{info_partner.id}"
        await callback.message.edit_text(text=f'{name_text} оценил стоимость решения'
                                              f' вопроса № {id_question} в {info_executor.cost} рублей. \n'
                                              f'Для выбора этого специалиста для решения вашего вопроса'
                                              f' оплатите указанную'
                                              f' стоимость и после успешной оплаты нажмите "Продолжить"',
                                         reply_markup=kb.keyboard_payment(payment_url=quickpay_base_url,
                                                                          payment_id=payment_id,
                                                                          amount=info_executor.cost,
                                                                          id_question=id_question))
    else:
        change_balance = info_executor.cost * -1
        await rq.update_user_balance(tg_id=callback.from_user.id,
                                     change_balance=change_balance)
        await state.update_data(id_question=id_question)
        await rq.set_subscribe_user(tg_id=callback.from_user.id)
        await rq.set_question_status(question_id=int(id_question),
                                     status=rq.QuestionStatus.work)
        info_user: User = await rq.get_user_by_id(tg_id=info_question.tg_id)
        info_partner: User = await rq.get_user_by_id(tg_id=info_question.partner_solution)
        await callback.message.delete()
        if info_partner.fullname != "none":
            name_text = info_partner.fullname
        else:
            name_text = f"специалистом #_{info_partner.id}"
        await callback.message.answer(text=f'Оплата вопроса № {info_question.id} списана с вашего баланса,'
                                           f' баланс составляет {info_user.balance}.\n'
                                           f'Между вами с {name_text} '
                                           f'для решения вопроса открыт диалог ,'
                                           f' все ваши сообщения будут перенаправлены ему.\n\n'
                                           f'Для завершения диалога нажмите "Завершить диалог"',
                                      reply_markup=kb.keyboard_finish_dialog())
        await bot.send_message(chat_id=info_question.partner_solution,
                               text=f'Пользователь #_{info_user.id} оплатил решение вопроса № {info_question.id}.\n'
                                    f'Между вами открыт диалог для решения вопроса,'
                                    f' все ваши сообщения будут перенаправлены ему.\n\n'
                                    f'Для завершения диалога нажмите "Завершить диалог"',
                               reply_markup=kb.keyboard_finish_dialog_partner())
        # reply_markup=kb.keyboard_open_dialog_user(id_question=id_question))
        data_dialog = {"tg_id_user": callback.from_user.id,
                       "tg_id_partner": info_question.partner_solution,
                       "id_question": int(id_question),
                       "status": rq.StatusDialog.active}
        id_dialog: int = await rq.add_dialog(data=data_dialog)
        result_: ForumTopic = await bot.create_forum_topic(chat_id=config.tg_bot.group_topic,
                                                           name=f'{id_question}:user/{callback.from_user.id}-partner'
                                                                f'/{info_question.partner_solution}')
        if info_question.content_ids == '':
            await bot.send_message(chat_id=config.tg_bot.group_topic,
                                   text=info_question.description,
                                   message_thread_id=result_.message_thread_id)
        else:
            content_id = info_question.content_ids
            typy_file = content_id.split('!')[0]
            if typy_file == 'photo':
                await bot.send_photo(chat_id=config.tg_bot.group_topic,
                                     photo=content_id.split('!')[1],
                                     caption=info_question.description,
                                     message_thread_id=result_.message_thread_id)
            elif typy_file == 'file':
                await bot.send_document(chat_id=config.tg_bot.group_topic,
                                        document=content_id.split('!')[1],
                                        caption=info_question.description,
                                        message_thread_id=result_.message_thread_id)
        await state.update_data(message_thread_id=result_.message_thread_id)
        await rq.set_dialog_active_tg_id_message(id_dialog=id_dialog,
                                                 message_thread_id=result_.message_thread_id)

    await bot.edit_message_text(chat_id=tg_id_partner,
                                message_id=info_executor.message_id,
                                text=f'Вас выбрал пользователь #_{info_user.id} для решения вопроса {id_question}',
                                reply_markup=None)
    executors: list[Executor] = await rq.get_executor_not(question_id=int(id_question), tg_id=int(tg_id_partner))
    list_executors: list = [executor for executor in executors]
    for executor in list_executors:
        try:
            await bot.send_message(chat_id=executor.tg_id,
                                   text=f'Специалист #_{info_partner.id} выбран для решения вопроса {id_question}')
            await bot.delete_message(chat_id=executor.tg_id,
                                     message_id=executor.message_id)
        except:
            pass
        try:
            await bot.delete_message(chat_id=callback.from_user.id,
                                     message_id=executor.message_id_cost)
        except:
            pass
        await rq.del_executor(question_id=int(id_question), tg_id=int(executor.tg_id))
    await callback.answer()


@router.callback_query(F.data.startswith('payquestion_'))
@router.callback_query(F.data.startswith('gratis_'))
async def check_pay_select_partner(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Проверка оплаты и обработка бесплатного диалога
    :param callback: payquestion_{id_question}_{payment_id}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'check_pay_select_partner {callback.message.chat.id}')
    if callback.data.startswith('payquestion_'):
        payment_id: str = callback.data.split('_')[-1]
        id_question: str = callback.data.split('_')[-2]
        result = await yoomany_chek_payment(payment_id=payment_id)
        if config.tg_bot.test == 'TRUE':
            result = True
        if result:
            await rq.set_question_status(question_id=int(id_question),
                                         status=rq.QuestionStatus.work)
            info_question: Question = await rq.get_question_id(question_id=int(id_question))
            info_executor: Executor = await rq.get_executor(question_id=int(id_question),
                                                            tg_id=info_question.partner_solution)
            await rq.update_user_balance(tg_id=callback.from_user.id,
                                         change_balance=info_executor.cost)
            await state.update_data(id_question=id_question)
            # увеличение заданного вопроса
            # await rq.set_subscribe_user(tg_id=callback.from_user.id)
            info_user: User = await rq.get_user_by_id(tg_id=info_question.tg_id)
            info_partner: User = await rq.get_user_by_id(tg_id=info_question.partner_solution)
            await callback.message.delete()
            if info_partner.fullname != "none":
                name_text = info_partner.fullname
            else:
                name_text = f"специалистом #_{info_partner.id}"
            await callback.message.answer(text=f'Оплата вопроса № {info_question.id} прошла успешно.\n'
                                               f'Между вами с {name_text} '
                                               f'для решения вопроса открыт диалог ,'
                                               f' все ваши сообщения будут перенаправлены ему.\n\n'
                                               f'Для завершения диалога нажмите "Завершить диалог"',
                                          reply_markup=kb.keyboard_finish_dialog())
            await bot.send_message(chat_id=info_question.partner_solution,
                                   text=f'Пользователь #_{info_user.id} оплатил решение вопроса № {info_question.id}.\n'
                                        f'Между вами открыт диалог для решения вопроса,'
                                        f' все ваши сообщения будут перенаправлены ему.\n\n'
                                        f'Для завершения диалога нажмите "Завершить диалог"',
                                   reply_markup=kb.keyboard_finish_dialog_partner())
                                   # reply_markup=kb.keyboard_open_dialog_user(id_question=id_question))
            data_dialog = {"tg_id_user": callback.from_user.id,
                           "tg_id_partner": info_question.partner_solution,
                           "id_question": int(id_question),
                           "status": rq.StatusDialog.active}
            id_dialog: int = await rq.add_dialog(data=data_dialog)
            result_: ForumTopic = await bot.create_forum_topic(chat_id=config.tg_bot.group_topic,
                                                               name=f'{id_question}:user/{callback.from_user.id}-partner'
                                                                    f'/{info_question.partner_solution}')
            if info_question.content_ids == '':
                await bot.send_message(chat_id=config.tg_bot.group_topic,
                                       text=info_question.description,
                                       message_thread_id=result_.message_thread_id)
            else:
                content_id = info_question.content_ids
                typy_file = content_id.split('!')[0]
                if typy_file == 'photo':
                    await bot.send_photo(chat_id=config.tg_bot.group_topic,
                                         photo=content_id.split('!')[1],
                                         caption=info_question.description,
                                         message_thread_id=result_.message_thread_id)
                elif typy_file == 'file':
                    await bot.send_document(chat_id=config.tg_bot.group_topic,
                                            document=content_id.split('!')[1],
                                            caption=info_question.description,
                                            message_thread_id=result_.message_thread_id)
            await state.update_data(message_thread_id=result_.message_thread_id)
            await rq.set_dialog_active_tg_id_message(id_dialog=id_dialog,
                                                     message_thread_id=result_.message_thread_id)
        else:
            await callback.answer(text='Платеж не прошел', show_alert=True)
    else:
        id_question: str = callback.data.split('_')[-1]
        tg_id_partner: str = callback.data.split('_')[1]
        await rq.set_question_status(question_id=int(id_question),
                                     status=rq.QuestionStatus.work)
        await rq.set_question_executor(question_id=int(id_question),
                                       executor=int(tg_id_partner))
        await state.update_data(id_question=id_question)
        await rq.set_subscribe_user(tg_id=callback.from_user.id)
        info_question: Question = await rq.get_question_id(question_id=int(id_question))
        info_user: User = await rq.get_user_by_id(tg_id=info_question.tg_id)
        info_partner: User = await rq.get_user_by_id(tg_id=int(tg_id_partner))
        await callback.message.delete()
        await callback.message.answer(text=f'Между вами со специалистом #_{info_partner.id} '
                                           f'для решения вопроса открыт диалог ,'
                                           f' все ваши сообщения будут перенаправлены ему.\n\n'
                                           f'Для завершения диалога нажмите "Завершить диалог"',
                                      reply_markup=kb.keyboard_finish_dialog())
        await bot.send_message(chat_id=info_question.partner_solution,
                               text=f'Пользователь #_{info_user.id} согласился на ваше предложения'
                                    f'для решения вопроса № {info_question.id}.\n'
                                    f'Между вами открыт диалог для решения вопроса,'
                                    f' все ваши сообщения будут перенаправлены ему.\n\n'
                                    f'Для завершения диалога нажмите "Завершить диалог"',
                               reply_markup=kb.keyboard_finish_dialog_partner())
        # reply_markup=kb.keyboard_open_dialog_user(id_question=id_question))
        data_dialog = {"tg_id_user": callback.from_user.id,
                       "tg_id_partner": info_question.partner_solution,
                       "id_question": int(id_question),
                       "status": rq.StatusDialog.active}
        id_dialog: int = await rq.add_dialog(data=data_dialog)
        result_: ForumTopic = await bot.create_forum_topic(chat_id=config.tg_bot.group_topic,
                                                           name=f'{id_question}:user/{callback.from_user.id}-partner'
                                                                f'/{info_question.partner_solution}')
        if info_question.content_ids == '':
            await bot.send_message(chat_id=config.tg_bot.group_topic,
                                   text=info_question.description,
                                   message_thread_id=result_.message_thread_id)
        else:
            content_id = info_question.content_ids
            typy_file = content_id.split('!')[0]
            if typy_file == 'photo':
                await bot.send_photo(chat_id=config.tg_bot.group_topic,
                                     photo=content_id.split('!')[1],
                                     caption=info_question.description,
                                     message_thread_id=result_.message_thread_id)
            elif typy_file == 'file':
                await bot.send_document(chat_id=config.tg_bot.group_topic,
                                        document=content_id.split('!')[1],
                                        caption=info_question.description,
                                        message_thread_id=result_.message_thread_id)
        await state.update_data(message_thread_id=result_.message_thread_id)
        await rq.set_dialog_active_tg_id_message(id_dialog=id_dialog,
                                                 message_thread_id=result_.message_thread_id)

# @router.callback_query(F.data.startswith('open_dialog_partner_'))
# async def open_dialog_partner(callback: CallbackQuery, state: FSMContext, bot: Bot):
#     """
#     Проверка оплаты
#     :param callback: open_dialog_partner_{id_question}
#     :param state:
#     :param bot:
#     :return:
#     """
#     logging.info(f'open_dialog_partner {callback.message.chat.id}')
#     id_question: str = callback.data.split('_')[-1]
#     info_question: Question = await rq.get_question_id(question_id=int(id_question))
#     await state.update_data(partner_dialog=info_question.partner_solution)
#     await state.update_data(id_question=id_question)
#     await state.set_state(StageSelectPartner.dialog_partner)
#     info_partner: User = await rq.get_user_by_id(tg_id=info_question.partner_solution)
#     await callback.message.answer(text=f'Вы открыли диалог со специалистом #_{info_partner.id},'
#                                        f' все ваши сообщения будут перенаправлены ему,'
#                                        f' для завершения диалога нажмите "Завершить диалог"',
#                                   reply_markup=kb.keyboard_finish_dialog())
#     await callback.answer()


@router.message(F.text == 'Завершить диалог')
@router.message(F.text == '/close_dialog')
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
    info_dialog: Dialog = await rq.get_dialog_active_tg_id(tg_id=message.from_user.id)
    if info_dialog:
        if message.from_user.id == info_dialog.tg_id_user:
            partner_dialog: int = info_dialog.tg_id_partner
            id_question: str = info_dialog.id_question
            info_partner: User = await rq.get_user_by_id(tg_id=partner_dialog)
            info_user: User = await rq.get_user_by_id(tg_id=info_dialog.tg_id_user)
            await bot.send_message(chat_id=partner_dialog,
                                   text=f'Диалог с пользователем #_{info_user.id} для решения вопроса'
                                        f' № {id_question} закрыт.',
                                   reply_markup=kb.keyboard_finish_dialog_main_menu())
            await message.answer(text=f'Диалог со специалистом #_{info_partner.id} для решения вопроса'
                                      f' № {id_question} закрыт.',
                                 reply_markup=kb.keyboard_finish_dialog_main_menu())
            await message.answer(text=f'Оцените качество решения вашего вопроса',
                                 reply_markup=kb.keyboard_quality_answer(question_id=int(id_question)))
            await rq.set_dialog_completed_tg_id(tg_id=message.from_user.id)
        elif message.from_user.id == info_dialog.tg_id_partner:
            user_dialog: int = info_dialog.tg_id_user
            id_question: str = info_dialog.id_question
            info_user: User = await rq.get_user_by_id(tg_id=user_dialog)
            info_partner: User = await rq.get_user_by_id(tg_id=info_dialog.tg_id_partner)
            await message.answer(
                text=f'Диалог с пользователем #_{info_user.id} для решения вопроса № {id_question} закрыт.',
                reply_markup=kb.keyboard_finish_dialog_main_menu())
            await bot.send_message(chat_id=user_dialog,
                                   text=f'Диалог со специалистом #_{info_partner.id} для решения вопроса'
                                        f' № {id_question} закрыт.',
                                   reply_markup=kb.keyboard_finish_dialog_main_menu())
            await bot.send_message(chat_id=user_dialog,
                                   text=f'Оцените качество решения вопроса № {id_question}',
                                   reply_markup=kb.keyboard_quality_answer(question_id=int(id_question)))
            await rq.set_dialog_completed_tg_id(tg_id=message.from_user.id)
    else:
        await message.answer(text='У вас нет активных диалогов')


@router.message(or_f(F.photo, F.text, F.document, F.video, F.voice), F.text != 'Выставить_счет')
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
    if message.text == '/get_logfile':
        file_path = "py_log.log"
        await message.answer_document(FSInputFile(file_path))

    if message.text == '/get_DB':
        file_path = "database/db.sqlite3"
        await message.answer_document(FSInputFile(file_path))
    info_dialog: Dialog = await rq.get_dialog_active_tg_id(tg_id=message.from_user.id)
    if info_dialog:
        dialog_chat_id = None
        if message.from_user.id == info_dialog.tg_id_user:
            dialog_chat_id = info_dialog.tg_id_partner
        elif message.from_user.id == info_dialog.tg_id_partner:
            dialog_chat_id = info_dialog.tg_id_user
    # data = await state.get_data()
    # partner_dialog = data['partner_dialog']
    # info_user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    # autor = f'Получено сообщение от пользователя #_{info_user.id}, для ответа откройте диалог с эти пользователем'
        if message.text:
            await bot.send_message(chat_id=dialog_chat_id,
                                   text=f'{message.text}')
            await bot.send_message(chat_id=config.tg_bot.group_topic,
                                   text=f'{message.from_user.id}:\n{message.text}',
                                   message_thread_id=info_dialog.message_thread_id)
        elif message.photo:
            photo_id = message.photo[-1].file_id
            await bot.send_photo(chat_id=dialog_chat_id,
                                 photo=photo_id,
                                 caption=f'{message.caption}')
            await bot.send_photo(chat_id=config.tg_bot.group_topic,
                                 photo=photo_id,
                                 caption=f'{message.from_user.id}:\n{message.caption}',
                                 message_thread_id=info_dialog.message_thread_id)
        elif message.document:
            document_id = message.document.file_id
            await bot.send_document(chat_id=dialog_chat_id,
                                    document=document_id,
                                    caption=f'{message.caption}')
            await bot.send_document(chat_id=config.tg_bot.group_topic,
                                    document=document_id,
                                    caption=f'{message.from_user.id}:\n{message.caption}',
                                    message_thread_id=info_dialog.message_thread_id)
        elif message.voice:
            voice_id = message.voice.file_id
            await bot.send_voice(chat_id=dialog_chat_id,
                                 voice=voice_id)
            await bot.send_voice(chat_id=config.tg_bot.group_topic,
                                 voice=voice_id,
                                 caption=f'{message.from_user.id}:',
                                 message_thread_id=info_dialog.message_thread_id)
        else:
            await message.answer(text=f'Такой контент отправить не могу, вы можете отправить:'
                                      f' текст, фото, аудио или документ')
    else:
        await message.answer(text='У вас нет активных диалогов')

