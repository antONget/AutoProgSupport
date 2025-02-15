from aiogram.types import CallbackQuery, Message
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from keyboards.partner import keyboard_account as kb
from filter.user_filter import IsRolePartner
from database import requests as rq
from database.models import Question, Executor, User, WithdrawalFunds
from utils.error_handling import error_handler
import logging
from datetime import datetime, timedelta

router = Router()


@router.callback_query(F.data.startswith('withdrawalfunds_'))
@error_handler
async def process_withdrawalfunds_admin(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Обработка запроса на списание администратором
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('process_withdrawalfunds_admin')
    action = callback.data.split('_')[1]
    id_withdrawal_funds = int(callback.data.split('_')[-2])
    info_withdrawal_funds: WithdrawalFunds = await rq.get_withdrawal_funds_id(id_=id_withdrawal_funds)
    summ_funds = int(callback.data.split('_')[-1])
    info_partner: User = await rq.get_user_by_id(tg_id=info_withdrawal_funds.tg_id_partner)
    if action == 'cancel':
        await callback.message.edit_text(text=f'Вы отклонили списание для'
                                              f' <a href="tg://user?id={info_partner.tg_id}>партнера</a>')
        await bot.send_message(chat_id=info_partner.tg_id,
                               text='Администратор отклонил списание')
        await rq.set_withdrawal_funds_status(id_=id_withdrawal_funds,
                                             status=rq.StatusWithdrawalFunds.cancel,
                                             balance_after=info_partner.balance,
                                             tg_id_admin=callback.from_user.id)
    elif action == 'confirm':
        await callback.message.edit_text(text=f'Вы подтвердили списание для'
                                              f' <a href="tg://user?id={info_partner.tg_id}>партнера</a>'
                                              f' на сумму {summ_funds} ₽')
        await bot.send_message(chat_id=info_partner.tg_id,
                               text=f'Администратор подтвердил списание {summ_funds} ₽')
        await rq.update_user_balance(tg_id=info_partner.tg_id,
                                     change_balance=summ_funds)
        info_partner: User = await rq.get_user_by_id(tg_id=info_withdrawal_funds.tg_id_partner)
        await rq.set_withdrawal_funds_status(id_=id_withdrawal_funds,
                                             status=rq.StatusWithdrawalFunds.completed,
                                             balance_after=info_partner.balance,
                                             tg_id_admin=callback.from_user.id)
