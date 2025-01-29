from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter

import keyboards.user.keyboards_rate as kb
import database.requests as rq
from database.models import User, Rate
from utils.error_handling import error_handler
from services.yookassa.payments import create_payment_yookassa, check_payment
from config_data.config import Config, load_config

import logging
from datetime import datetime, timedelta

config: Config = load_config()
router = Router()


@router.message(F.text == 'Тарифы')
@error_handler
async def press_button_rate(message: Message, bot: Bot) -> None:
    """
    Выбор тарифа для подписки
    :param message:
    :param bot:
    :return:
    """
    logging.info(f'press_button_rate: {message.chat.id}')
    list_rate: list[Rate] = await rq.get_list_rate()
    await message.answer(text=f'Краткое описание тарифов! Например, Тариф - 1, вы можете задать 3 вопроса',
                         reply_markup=kb.keyboards_select_rate(list_rate=list_rate))


@router.callback_query(F.data.startswith('select_rate_'))
@error_handler
async def select_rate(callback: CallbackQuery, bot: Bot):
    """
    Обработка выбранного тарифа
    1. Формирование счета на оплату
    2. Отправка ссылки для проведения платежа
    :param callback:
    :param bot:
    :return:
    """
    logging.info('select_rate')
    rate_id = callback.data.split('_')[-1]
    rate_info = await rq.get_rate_id(rate_id=int(rate_id))
    payment_url, payment_id = create_payment_yookassa(amount=rate_info.amount_rate,
                                                      chat_id=callback.from_user.id,
                                                      content=rate_info.title_rate)
    await callback.message.edit_text(text=f'Оплатите доступ к боту согласно выбранного тарифа',
                                     reply_markup=kb.keyboard_payment(payment_url=payment_url,
                                                                      payment_id=payment_id,
                                                                      amount=rate_info.amount_rate,
                                                                      rate_id=rate_id))
    await callback.answer()


@router.callback_query(F.data.startswith('payment_'))
async def check_pay(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Проверка оплаты
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'check_pay {callback.message.chat.id}')
    payment_id = callback.data.split('_')[-1]
    rate_id = callback.data.split('_')[-2]
    rate_info = await rq.get_rate_id(rate_id=int(rate_id))
    result = check_payment(payment_id=payment_id)
    # result = 'succeeded'
    if result == 'succeeded':
        await callback.message.delete()
        current_date = datetime.now()
        current_date_str = current_date.strftime('%d-%m-%Y %H:%M')
        date_completion = current_date + timedelta(days=rate_info.duration_rate)
        date_completion_str = date_completion.strftime('%d-%m-%Y %H:%M')
        await callback.answer(text='Платеж прошел успешно', show_alert=True)
        data_subscribe = {'tg_id': callback.from_user.id,
                          'rate_id': int(rate_id),
                          'date_start': current_date_str,
                          'date_completion': date_completion_str,
                          'count_question': 0}
        await rq.add_subscribe(data=data_subscribe)
        await callback.message.answer(text=f'Добро пожаловать, {callback.from_user.username}!\n\n'
                                           f'<b>Ваш тариф:</b> {rate_info.title_rate}\n'
                                           f'<b>Срок подписки:</b> {date_completion_str}\n'
                                           f'<b>Количество вопросов:</b> 0/{rate_info.question_rate}',
                                      reply_markup=kb.keyboard_send_question())
    else:
        await callback.answer(text=f'Платеж не подтвержден, если вы совершили платеж, то попробуйте проверить'
                                   f' его немного позднее или обратитесь в "Поддержку"',
                              show_alert=True)
    await callback.answer()
