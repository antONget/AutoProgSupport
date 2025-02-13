from aiogram.types import CallbackQuery, Message
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from utils.error_handling import error_handler
from filter.user_filter import IsRolePartner
from services.yoomany.quickpay import yoomany_chek_payment, yoomany_payment
from database.models import User, Dialog, Question, Executor
from database.requests import get_user_by_id, get_dialog_active_tg_id, get_question_id, get_executor,\
    update_user_balance, update_cost_executor
from keyboards.partner.keyboard_send_receipt import keyboard_payment_receipt, keyboard_payment_receipt_balance
import logging
from config_data.config import Config, load_config

router = Router()

config: Config = load_config()


class StateReceipt(StatesGroup):
    amount_receipt = State()


@router.message(F.text == 'Выставить_счет', )
@error_handler
async def press_send_receipt(message: Message, state: FSMContext):
    """
    Выставление счета на оплату пользователем
    :param message:
    :param state:
    :return:
    """
    logging.info('press_send_receipt')
    await state.set_state(state=None)
    await message.answer(text='Пришлите сумму для выставления счета клиенту')
    await state.set_state(StateReceipt.amount_receipt)


@router.message(F.text, StateFilter(StateReceipt.amount_receipt))
@error_handler
async def get_amount_receipt(message: Message, state: FSMContext, bot: Bot):
    """
    Получение суммы для оплаты
    :param message:
    :param state:
    :param bot:
    :return:
    """
    amount_receipt = message.text
    if amount_receipt.isdigit():
        await state.update_data(amount_receipt=int(amount_receipt))
        await state.set_state(state=None)
        info_partner: User = await get_user_by_id(tg_id=message.from_user.id)
        info_dialog: Dialog = await get_dialog_active_tg_id(tg_id=message.from_user.id)
        info_user: User = await get_user_by_id(tg_id=info_dialog.tg_id_user)
        if info_dialog:
            await update_cost_executor(question_id=info_dialog.id_question,
                                       tg_id=message.from_user.id,
                                       cost=int(amount_receipt))

            quickpay_base_url, quickpay_redirected_url, payment_id = await yoomany_payment(amount=int(amount_receipt))
            if info_partner.fullname != "none":
                name_text = info_partner.fullname
            else:
                name_text = f"Специалист #_{info_partner.id}"
            if info_user.balance < int(amount_receipt):
                await bot.send_message(chat_id=info_dialog.tg_id_user,
                                       text=f'{name_text} выставил счет для решения вопроса'
                                            f' вопроса № {info_dialog.id_question} в {amount_receipt} рублей. \n'
                                            f'После успешной оплаты нажмите "Продолжить"',
                                       reply_markup=keyboard_payment_receipt(payment_url=quickpay_base_url,
                                                                             payment_id=payment_id,
                                                                             amount=amount_receipt,
                                                                             id_question=info_dialog.id_question))
            else:
                await bot.send_message(chat_id=info_dialog.tg_id_user,
                                       text=f'{name_text} выставил счет для решения вопроса'
                                            f' вопроса № {info_dialog.id_question} в {amount_receipt} рублей. \n'
                                            f'На вашем балансе {info_user.balance} рублей,'
                                            f' можете списать с него сумму для оплаты счета'
                                            f' или оплатить'
                                            f'После успешной оплаты нажмите "Продолжить"',
                                       reply_markup=keyboard_payment_receipt_balance(payment_url=quickpay_base_url,
                                                                                     payment_id=payment_id,
                                                                                     amount=amount_receipt,
                                                                                     id_question=info_dialog.id_question))
            await message.answer(text='Счет направлен клиенту')
    else:
        await message.answer(text='Сумма для выставления счета должна быть целым числом, повторите ввод данных')


@router.callback_query(F.data.startswith('sendreceipt_'))
@router.callback_query(F.data.startswith('debited_'))
@error_handler
async def check_pay_receipt(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Проверка оплаты
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'check_pay_receipt {callback.message.chat.id}')
    payment_id: str = callback.data.split('_')[-1]
    id_question: str = callback.data.split('_')[-2]
    amount_receipt: int = int(callback.data.split('_')[-3])
    result = await yoomany_chek_payment(payment_id=payment_id)
    if config.tg_bot.test == 'TRUE' or callback.data.startswith('debited_'):
        result = True
    if result:
        info_question: Question = await get_question_id(question_id=int(id_question))
        info_user: User = await get_user_by_id(tg_id=callback.from_user.id)
        await update_user_balance(tg_id=callback.from_user.id,
                                  change_balance=amount_receipt)
        await callback.message.edit_text(text=f'Оплата счета на сумму {amount_receipt} для решения вопроса'
                                              f' № {info_question.id} прошла успешно.',
                                         reply_markup=None)
        await bot.send_message(chat_id=info_question.partner_solution,
                               text=f'Пользователь #_{info_user.id} оплатил счет на сумму {amount_receipt}'
                                    f'для решения вопроса № {info_question.id}.')
