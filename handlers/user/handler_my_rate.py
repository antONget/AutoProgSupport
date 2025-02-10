from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import keyboards.user.keyboards_rate as kb
import database.requests as rq
from database.models import Rate, Subscribe
from utils.error_handling import error_handler
from config_data.config import Config, load_config

import logging
from datetime import datetime

config: Config = load_config()
router = Router()
router.message.filter(F.chat.type == "private")


class QuestionState(StatesGroup):
    question = State()


# Персонал
@router.message(F.text == 'Задать вопрос')
@error_handler
async def press_button_my_rate(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Проверка тарифа
    :param message:
    :param bot:
    :return:
    """
    logging.info(f'press_button_my_rate: {message.chat.id}')
    await message.answer(text=f'В этом разделе вы можете задать вопрос специалистам',
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
                                  f'Пришлите описание вашей проблемы, можете добавить фото или файл 📎 .',
                             reply_markup=None)
                             # reply_markup=kb.keyboard_send_question())
        await state.set_state(QuestionState.question)
        await state.update_data(content='')
        # await state.update_data(count=[])
        await state.update_data(task='')
