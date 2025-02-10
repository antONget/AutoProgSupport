from aiogram.types import CallbackQuery, Message
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter

from keyboards.partner import keyboard_account as kb
from filter.user_filter import IsRolePartner
from database import requests as rq
from database.models import Question, Executor, User
from utils.error_handling import error_handler
import logging

router = Router()


class StateAccount(StatesGroup):
    fullname = State()


@router.message(F.text == 'Личный кабинет', IsRolePartner())
@error_handler
async def process_buttons_account(message: Message, state: FSMContext, bot: Bot):
    """
    Личный кабинет партнера
    :param message:
    :param state:
    :param bot
    :return:
    """
    logging.info('process_buttons_account')
    info_partner: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    await message.answer(text=f'В этом разделе ПАРТНЕР может изменить персональные данные, отображаемые пользователям',
                         reply_markup=kb.keyboard_partner_account(info_partner=info_partner))


@router.callback_query(F.data.startswith('fullname_'))
@error_handler
async def change_account(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Получаем поле которое нужно обновить
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_account')
    await callback.message.edit_text(text=f'Пришлите новое значение:')
    await state.set_state(StateAccount.fullname)


@router.message(F.text, StateFilter(StateAccount.fullname))
@error_handler
async def get_fullname(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем имя партнера
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_fullname')
    fullname = message.text
    await rq.set_user_fullname(tg_id=message.from_user.id,
                               fullname=fullname)
    await state.set_state(state=None)
    await process_buttons_account(message=message, state=state, bot=bot)
