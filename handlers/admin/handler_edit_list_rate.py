from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter

import keyboards.admin.keyboards_edit_list_rate as kb
import database.requests as rq
from database.models import User, Rate
from filter.admin_filter import IsSuperAdmin
from utils.error_handling import error_handler


import asyncio
import logging


router = Router()


class RateState(StatesGroup):
    title_rate = State()
    amount_rate = State()
    duration_rate = State()
    question_rate = State()


@router.message(F.text == 'Тарифы', IsSuperAdmin())
@error_handler
async def process_change_list_rate(message: Message, bot: Bot) -> None:
    """
    Действие с тарифом
    :param message:
    :param bot:
    :return:
    """
    logging.info(f'process_change_list_rate: {message.chat.id}')
    await message.answer(text="Добавить или удалить тариф",
                         reply_markup=kb.keyboard_select_action_rate())


@router.callback_query(F.data.startswith('rate_action_'))
@error_handler
async def process_select_action(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Выбор действия которое нужно совершить с тарифом
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_add_admin: {callback.message.chat.id}')
    action = callback.data.split('_')[-1]
    if action == 'add':
        await callback.message.edit_text(text='Пришлите название тарифа',
                                         reply_markup=None)
        await state.set_state(RateState.title_rate)
    elif action == 'del':
        list_rate: list[Rate] = await rq.get_list_rate()
        await callback.message.edit_text(text='Выберите тариф для удаления',
                                         reply_markup=kb.keyboards_del_rate(list_rate=list_rate))
    await callback.answer()


@router.callback_query(F.data.startswith('rate_select_del_'))
@error_handler
async def process_rate_delete(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Удаление выбранного тарифа
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_rate_delete: {callback.message.chat.id}')
    rate_id = int(callback.data.split('_')[-1])
    await rq.rate_delete_id(rate_id=rate_id)
    await callback.message.edit_text(text=f'Тариф успешно удален',
                                     reply_markup=None)


@router.message(F.text, StateFilter(RateState.title_rate))
@router.message(F.text, StateFilter(RateState.amount_rate))
@router.message(F.text, StateFilter(RateState.duration_rate))
@router.message(F.text, StateFilter(RateState.question_rate))
@error_handler
async def get_title_rate(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем название тарифа
    :param message:
    :param state:
    :param bot:
    :return:
    """
    if message.text in ['Отчет', 'Партнеры', 'Тарифы']:
        await message.answer(text='Изменение списка тарифов прервано')
        await state.set_state(state=None)
        return
    current_state = await state.get_state()
    if current_state == RateState.title_rate:
        title_rate = message.text
        await state.update_data(title_rate=title_rate)
        await message.answer(text=f'Укажите стоимость для тарифа <b>{title_rate}</b>')
        await state.set_state(RateState.amount_rate)
    elif current_state == RateState.amount_rate:
        if message.text.isdigit():
            amount_rate = int(message.text)
            await state.update_data(amount_rate=amount_rate)
            data = await state.get_data()
            title_rate = data['title_rate']
            await message.answer(text=f'Укажите длительность для тарифа <b>{title_rate}</b>')
            await state.set_state(RateState.duration_rate)
        else:
            await message.answer(text='Некорректно введены данные. Стоимость тарифа должна быть целым числом')
            return
    elif current_state == RateState.duration_rate:
        if message.text.isdigit():
            duration_rate = int(message.text)
            await state.update_data(duration_rate=duration_rate)
            data = await state.get_data()
            title_rate = data['title_rate']
            await message.answer(text=f'Укажите количество вопросов для тарифа <b>{title_rate}</b>')
            await state.set_state(RateState.question_rate)
        else:
            await message.answer(text='Некорректно введены данные. Длительность тарифа должна быть целым числом')
            return
    elif current_state == RateState.question_rate:
        if message.text.isdigit():
            question_rate = int(message.text)
            await state.update_data(question_rate=question_rate)
            data = await state.get_data()
            data_rate = {"title_rate": data["title_rate"],
                         "amount_rate": data["amount_rate"],
                         "duration_rate": data["duration_rate"],
                         "question_rate": data["duration_rate"]}
            await rq.add_rate(data=data_rate)
            await message.answer(text=f'Тариф <b>{data["title_rate"]}</b> стоимостью {data["amount_rate"]},'
                                      f' длительностью {data["duration_rate"]} на {data["duration_rate"]} вопрос'
                                      f' добавлен')
            await state.set_state(state=None)
        else:
            await message.answer(text='Некорректно введены данные. Длительность тарифа должна быть целым числом')
            return




