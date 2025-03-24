from aiogram.types import CallbackQuery, Message
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f

from keyboards.partner import keyboard_account as kb
from filter.user_filter import IsRolePartnerDB, IsRoleAdmin
from filter.admin_filter import IsSuperAdmin
from database import requests as rq
from database.models import Question, Executor, User
from utils.error_handling import error_handler
from utils.send_admins import send_message_admins
import logging
from datetime import datetime, timedelta

router = Router()


class StateAccount(StatesGroup):
    fullname = State()
    withdrawal_funds = State()


@router.message(F.text == 'Личный кабинет', or_f(IsSuperAdmin(), IsRolePartnerDB()))
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
                         reply_markup=await kb.keyboard_partner_account(info_partner=info_partner))


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


@router.callback_query(F.data.startswith('balancepartner_'))
@error_handler
async def press_balance_partner(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Получаем поле которое нужно обновить
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('press_balance_partner')
    info_partner: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
    question_list: list[Question] = await rq.get_questions_tg_id(partner_solution=callback.from_user.id)
    total_balance = []
    current_balance = info_partner.balance
    month_balance = []
    week_balance = []
    current_day_month = datetime.now() - timedelta(days=datetime.now().day)
    current_day_week = datetime.now() - timedelta(days=datetime.now().weekday())
    for question in question_list:
        executor: Executor = await rq.get_executor(question_id=question.id,
                                                   tg_id=question.partner_solution)
        if question.date_solution:
            date_question = datetime(year=int(question.date_solution.split('-')[2].split()[0]),
                                     month=int(question.date_solution.split('-')[1]),
                                     day=int(question.date_solution.split('-')[0]))
            if date_question >= current_day_week:
                week_balance.append(executor.cost)
            if date_question >= current_day_month:
                month_balance.append(executor.cost)
        total_balance.append(executor.cost)
    await callback.message.edit_text(text=f'Ваш текущий баланс составляет: {current_balance} ₽\n\n'
                                          f'Заработали за:\n'
                                          f'Неделю: {sum(week_balance)} ₽\n'
                                          f'Месяц: {sum(month_balance)} ₽\n'
                                          f'Все время: {sum(total_balance)} ₽\n')


@router.callback_query(F.data.startswith('request_withdrawal_funds'))
@error_handler
async def press_request_withdrawal_funds(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Запросить вывод средств
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('press_request_withdrawal_funds')
    info_partner: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
    current_balance = info_partner.balance
    if current_balance >= 1000:
        await callback.message.edit_text(text=f'Ваш текущий баланс составляет: {current_balance} ₽\n\n'
                                              f'Введите сумму для вывода не менее 1000 рублей')
        await state.set_state(StateAccount.withdrawal_funds)
    else:
        await callback.message.edit_text(text=f'Ваш текущий баланс составляет: {current_balance} ₽\n\n'
                                              f'Вывести можно не менее 1000 рублей')


@router.message(F.text, StateFilter(StateAccount.withdrawal_funds))
@error_handler
async def get_withdrawal_funds(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем сумму для вывода средств с баланса
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_withdrawal_funds {message.from_user.id}')
    summ_funds = message.text
    if summ_funds.isdigit():
        info_partner: User = await rq.get_user_by_id(tg_id=message.from_user.id)
        current_balance = info_partner.balance
        if int(summ_funds) < current_balance:
            await state.update_data(summ_funds=int(summ_funds))
            await message.answer(text='Пришлите реквизиты для вывода средств')
        else:
            await message.answer(text='Сумма указана не корректна, повторите ввод')
    else:
        await message.answer(text='Сумма указана не корректна, повторите ввод')


@router.message(F.text, StateFilter(StateAccount.withdrawal_funds))
@error_handler
async def get_withdrawal_funds(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем сумму для вывода средств с баланса
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_withdrawal_funds {message.from_user.id}')
    info_partner: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    if info_partner.fullname != "none":
        name_text = info_partner.fullname
    else:
        name_text = f"#_{info_partner.id}"
    data = await state.update_data()
    dict_withdrawal_funds = {"tg_id_partner": message.from_user.id,
                             "summ_withdrawal_funds": data["summ_funds"],
                             "data_withdrawal": datetime.now().strftime('%d.%m.%Y %H:%M'),
                             "balance_before": info_partner.balance,
                             "requisites": message.text}
    id_: int = await rq.add_withdrawal_funds(data=dict_withdrawal_funds)
    await bot.send_message(chat_id=1492644981,
                           text=f'Партнер <a href="tg://user?id={message.from_user.id}">{name_text}</a> '
                                f'запросил вывод средств в размере {data["summ_funds"]}, на балансе партнера '
                                f'{info_partner.balance} ₽\n'
                                f'Реквизиты для вывода: {message.text}',
                           reply_markup=kb.keyboard_request_withdrawal_funds(id_=id_,
                                                                             summ_funds=data["summ_funds"]))
    await bot.send_message(chat_id=843554518,
                           text=f'Партнер <a href="tg://user?id={message.from_user.id}">{name_text}</a> '
                                f'запросил вывод средств в размере {data["summ_funds"]}, на балансе партнера '
                                f'{info_partner.balance} ₽\n'
                                f'Реквизиты для вывода: {message.text}',
                           reply_markup=kb.keyboard_request_withdrawal_funds(id_=id_,
                                                                             summ_funds=data["summ_funds"]))
    await message.answer(text=f'Запрос на вывод средств отправлен администратору')
    await state.set_state(state=None)


@router.callback_query(F.data == 'rating_partner')
@error_handler
async def press_rating_partner(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Получаем рейтинг партнера
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('press_rating_partner')
    info_partner: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
    questions_list: list[Question] = await rq.get_questions_tg_id(partner_solution=info_partner.tg_id)
    if len(questions_list):
        quality_dict = {}
        total_quality = 0
        for question in questions_list:
            total_quality += question.quality
            if quality_dict.get(question.quality, False):
                quality_dict[question.quality] += 1
            else:
                quality_dict[question.quality] = 1
        average_rating = round(total_quality/len(questions_list), 1)
        text_rating = ''
        for k, v in dict(sorted(quality_dict.items(), reverse=True)).items():
            if 10 <= v % 100 < 20 or v % 10 > 4 or v % 10 == 0:
                ending = 'ов'
            elif v % 10 == 1:
                ending = ''
            else:
                ending = 'a'
            text_rating += f'{k} ⭐️: {v} вопрос{ending}\n'
        await callback.message.edit_text(text=f'Ваш рейтинг составляет: {average_rating} ⭐️\n\n'
                                              f'{text_rating}')
    else:
        await callback.message.edit_text(text=f'У вас нет завершенных заказов')
