from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f

import keyboards.partner.keyboard_dialog_partner as kb
import database.requests as rq
from database.models import User, Rate, Subscribe, Question
from utils.error_handling import error_handler



from config_data.config import Config, load_config

import logging


config: Config = load_config()
router = Router()


class StageSelectUser(StatesGroup):
    dialog_user = State()


@router.callback_query(F.data.startswith('open_dialog_user_'))
async def open_dialog_user(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Проверка оплаты
    :param callback: open_dialog_partner_{id_question}
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'open_dialog_user {callback.message.chat.id}')
    id_question: str = callback.data.split('_')[-1]
    info_question: Question = await rq.get_question_id(question_id=int(id_question))
    await state.update_data(user_dialog=info_question.tg_id)
    await state.update_data(id_question=id_question)
    await state.set_state(StageSelectUser.dialog_user)
    info_user: User = await rq.get_user_by_id(tg_id=info_question.tg_id)
    await callback.message.answer(text=f'Вы открыли диалог с пользователем #_{info_user.id},'
                                       f' все ваши сообщения будут перенаправлены ему,'
                                       f' для завершения диалога нажмите "Завершить диалог"',
                                  reply_markup=kb.keyboard_finish_dialog())
    await callback.answer()


@router.message(StateFilter(StageSelectUser.dialog_user), F.text == 'Завершить диалог')
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
    user_dialog: int = data['user_dialog']
    id_question: str = data['id_question']
    info_user: User = await rq.get_user_by_id(tg_id=user_dialog)
    await message.answer(text=f'Диалог с пользователем #_{info_user.id} для решения вопроса № {id_question} закрыт.',
                         reply_markup=kb.keyboard_finish_dialog_main_menu())
    await bot.send_message(chat_id=user_dialog,
                           text=f'Оцените качество решения вопроса № {id_question}',
                           reply_markup=kb.keyboard_quality_answer(question_id=int(id_question)))


@router.message(StateFilter(StageSelectUser.dialog_user), or_f(F.photo, F.text, F.document, F.video))
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
    user_dialog = data['user_dialog']
    info_user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    autor = f'Получено сообщение от специалиста #_{info_user.id}, для ответа откройте диалог с эти специалистом'
    if message.text:
        await bot.send_message(chat_id=user_dialog,
                               text=f'{autor}\n\n'
                                    f'{message.text}')
    elif message.photo:
        photo_id = message.photo[-1].file_id
        await bot.send_photo(chat_id=user_dialog,
                             photo=photo_id,
                             caption=f'{autor}\n\n{message.caption}')
    elif message.document:
        document_id = message.document.file_id
        await bot.send_document(chat_id=user_dialog,
                                document=document_id,
                                caption=f'{autor}\n\n{message.caption}')
    else:
        await message.answer(text='Такой контент отправить не могу, вы можете отправить: текст, фото или документ')

