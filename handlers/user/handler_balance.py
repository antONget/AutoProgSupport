from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup


import keyboards.user.keyboards_balance as kb
import database.requests as rq
from database.models import User
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from services.yoomany.quickpay import yoomany_payment, yoomany_chek_payment

import logging


config: Config = load_config()
router = Router()
router.message.filter(F.chat.type == "private")


class StateBalance(StatesGroup):
    replenish = State()


@router.message(F.text == 'Баланс')
@error_handler
async def press_button_rate(message: Message, bot: Bot) -> None:
    """
    Проверка баланса пользователя
    :param message:
    :param bot:
    :return:
    """
    logging.info(f'press_button_rate: {message.chat.id}')
    info_user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    await message.answer(text=f'Ваш баланс составляет <b>{info_user.balance}</b> рублей',
                         reply_markup=kb.keyboard_replenish_balance())


@router.callback_query(F.data == 'replenish_balance')
@error_handler
async def replenish_balance(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Пополнение баланса
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('replenish_balance')
    await callback.message.edit_text(text='Пришлите сумму для пополнения баланса')
    await state.set_state(StateBalance.replenish)


@router.message(StateFilter(StateBalance.replenish))
@error_handler
async def get_summ_replenish(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем сумму пополнения
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_summ_replenish')
    summ_replenish = message.text
    if summ_replenish.isdigit() and int(summ_replenish) > 0:
        quickpay_base_url, quickpay_redirected_url, payment_id = await yoomany_payment(amount=int(summ_replenish))
        await message.answer(text=f'Счет на пополнение баланса. Произведите пополнение и нажмите "Продолжить"',
                             reply_markup=kb.keyboard_payment(payment_url=quickpay_base_url,
                                                              payment_id=payment_id,
                                                              amount=summ_replenish))
        await state.set_state(state=None)
    else:
        await message.answer(text='Некорректно указана сумма пополнения баланса')


@router.callback_query(F.data.startswith('pay_replenish_'))
async def check_pay(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Проверка пополнения баланса
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'check_pay {callback.message.chat.id}')
    payment_id = callback.data.split('_')[-1]
    summ = int(callback.data.split('_')[-2])
    result = await yoomany_chek_payment(payment_id=payment_id)
    if config.tg_bot.test == 'TRUE':
        result = 'succeeded'
    if result == 'succeeded':
        await rq.update_user_balance(tg_id=callback.from_user.id, change_balance=summ)
        info_user: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
        await callback.message.edit_text(text=f'Баланс успешно пополнен и составляет: {info_user.balance} рублей')
