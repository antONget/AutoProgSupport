from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

import keyboards.user.keyboards_rate as kb
from keyboards.user.keyboards_my_rate import keyboard_ask_typy, keyboard_ask_master
import database.requests as rq
from database.models import Rate, Subscribe
from utils.error_handling import error_handler
from config_data.config import Config, load_config
from services.openai.tg_assistant import send_message_to_openai

import logging
from datetime import datetime

config: Config = load_config()
router = Router()
router.message.filter(F.chat.type == "private")


class QuestionState(StatesGroup):
    question = State()
    question_GPT = State()


# Персонал
@router.message(F.text == 'Задать вопрос')
@error_handler
async def press_button_my_rate(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Проверка тарифа
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'press_button_my_rate: {message.chat.id}')
    await message.answer(text=f'В этом разделе вы можете задать свой вопрос',
                         reply_markup=kb.keyboard_main_menu())
    # проверка на наличие активной подписки
    subscribes: list[Subscribe] = await rq.get_subscribes_user(tg_id=message.from_user.id)
    active_subscribe = False
    if subscribes:
        last_subscribe: Subscribe = subscribes[-1]
        date_format = '%d-%m-%Y %H:%M'
        current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        delta_time = (datetime.strptime(current_date, date_format) -
                      datetime.strptime(last_subscribe.date_completion, date_format))
        rate: Rate = await rq.get_rate_id(rate_id=last_subscribe.rate_id)
        if delta_time.days < rate.duration_rate:
            rate: Rate = await rq.get_rate_id(rate_id=last_subscribe.rate_id)
            if last_subscribe.count_question < rate.question_rate:
                active_subscribe = True
    # если нет подписок или подписки не активны
    if not subscribes or not active_subscribe:
        list_rate: list[Rate] = await rq.get_list_rate()
        await message.answer(text=f'У вас нет активных подписок. Выберите подходящий тариф!',
                             reply_markup=kb.keyboards_select_rate(list_rate=list_rate))
    else:
        last_subscribe: Subscribe = subscribes[-1]
        rate_info: Rate = await rq.get_rate_id(rate_id=last_subscribe.rate_id)
        await message.answer(text=f'<b>Ваш тариф:</b> {rate_info.title_rate}\n'
                                  f'<b>Срок подписки:</b> {last_subscribe.date_completion}\n'
                                  f'<b>Количество вопросов:</b> {last_subscribe.count_question}/{rate_info.question_rate}\n\n'
                                  f'Выберите кому вы бы хотели адресовать вопрос',
                             reply_markup=keyboard_ask_typy())


@router.callback_query(F.data.startswith('ask'))
async def get_type_ask(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """"
    Получаем кому адресован вопрос
    """
    logging.info('get_type_ask')
    type_ask = callback.data.split('_')[-1]
    if type_ask == 'master':
        await state.set_state(QuestionState.question)
        await state.update_data(content='')
        await callback.message.edit_text(text='Пришлите описание вашей проблемы, можете добавить фото или файл 📎 .')
        await state.update_data(task='')
    else:
        await callback.message.delete()
        await callback.message.answer(text=f'Задай свой вопрос chatGPT',
                                      reply_markup=keyboard_ask_master())
        await state.set_state(QuestionState.question_GPT)
    await callback.answer()


@router.message(F.text == 'Задать вопрос специалисту')
@error_handler
async def press_ask_master(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Перевод вопроса мастеру
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'press_ask_master: {message.chat.id}')
    await state.set_state(QuestionState.question)
    await state.update_data(content='')
    await message.answer(text='Пришлите описание вашей проблемы, можете добавить фото или файл 📎 .')
    await state.update_data(task='')


@router.message(StateFilter(QuestionState.question_GPT))
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
        await message.answer(text="⏳ Думаю...")
        result = send_message_to_openai(user_id=message.from_user.id,
                                        user_input=message.text)
        await message.answer(text=result)


