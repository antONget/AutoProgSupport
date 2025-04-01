from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter


from keyboards.user.keyboards_assistant_gpt import keyboard_ask_typy, keyboard_ask_master, keyboard_period_gpt, \
    keyboard_payment_gpt, keyboard_main_menu
import database.requests as rq
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from services.openai.tg_assistant import send_message_to_openai
from services.yoomany.quickpay import yoomany_payment, yoomany_chek_payment

import logging
from datetime import datetime, timedelta

config: Config = load_config()
router = Router()
router.message.filter(F.chat.type == "private")


class GPTState(StatesGroup):
    question_GPT = State()


@router.callback_query(F.data == 'ask_artificial_intelligence')
async def ask_artificial_intelligence(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Получаем кому следует адресовать вопрос
    :param callback: ask_artificial_intelligence, ask_master
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_type_ask')
    await callback.message.delete()
    await callback.message.answer(text=f'Задай свой вопрос ИИ AUTOPROG',
                                  reply_markup=keyboard_ask_master())
    await state.set_state(GPTState.question_GPT)
    await rq.add_user_question_gpt(data={"tg_id_user": callback.from_user.id})
    await callback.answer()


@router.message(StateFilter(GPTState.question_GPT))
@error_handler
async def get_question_gpt(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем вопрос
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_question_gpt')
    question_gpt = message.text
    if question_gpt in ['Тарифы', 'Задать вопрос', 'Баланс', '/cancel']:
        await state.set_state(state=None)
        await message.answer(text='Диалог с GPT прерван')
        return
    else:
        if await rq.check_limit_free(tg_id=message.from_user.id) or\
                await rq.check_date_payment(tg_id=message.from_user.id):
            await message.answer(text="⏳ Думаю...")
            result = send_message_to_openai(user_id=message.from_user.id,
                                            user_input=message.text)
            await message.answer(text=result)
        else:
            await message.answer(text='Вы исчерпали лимит вопросов для ИИ,'
                                      ' вы можете приобрести доступ к ИИ или обратиться к специалистам',
                                 reply_markup=keyboard_period_gpt())


@router.callback_query(F.data.startswith('period_payment_gpt_'))
@error_handler
async def process_payment_gpt(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Получаем вопрос
    :param callback: period_payment_gpt_week, period_payment_gpt_month
    :param state:
    :param bot:
    :return:
    """
    logging.info('process_payment_gpt')
    period_payment_gpt = callback.data.split('_')[-1]
    amount = 300
    if period_payment_gpt == 'month':
        amount = 1000
    quickpay_base_url, quickpay_redirected_url, payment_id = await yoomany_payment(amount=amount)
    await callback.message.edit_text(
        text=f'Чтобы оплатить доступ к ИИ оплатите {amount} рублей и нажмите "Продолжить"',
        reply_markup=keyboard_payment_gpt(payment_url=quickpay_base_url,
                                          payment_id=payment_id,
                                          amount=str(amount),
                                          period=period_payment_gpt))


@router.callback_query(F.data.startswith('gptpayment_'))
@error_handler
async def check_pay_gpt(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Проверка оплаты
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'check_pay_gpt {callback.from_user.id}')
    payment_id = callback.data.split('_')[-1]
    period_payment_gpt = callback.data.split('_')[-2]
    result = True
    if config.tg_bot.test == 'FALSE':
        result = await yoomany_chek_payment(payment_id=payment_id)
    if config.tg_bot.support_id == str(callback.from_user.id):
        result = True
    if result:
        await callback.message.delete()
        period = 7
        if period_payment_gpt == 'month':
            period = 30
        date_access_free = datetime.now() + timedelta(days=period)
        date_payment = date_access_free.strftime('%d.%m.%Y')
        await rq.update_date_access_free_gpt(tg_id=callback.from_user.id,
                                             date_payment=date_payment)
        await callback.message.answer(text=f'Платеж прошел успешно',
                                      reply_markup=keyboard_main_menu())
        await callback.message.edit_text(text=f'доступ к ИИ AUTOPROG открыт до {date_payment}',
                                         reply_markup=keyboard_ask_typy())
    else:
        await callback.answer(text=f'Платеж не подтвержден, если вы совершили платеж, то попробуйте проверить'
                                   f' его немного позднее или обратитесь в "Поддержку"',
                              show_alert=True)
    await callback.answer()
