from aiogram import F, Router, Bot
from aiogram.types import Message

import keyboards.user.keyboards_rate as kb
import database.requests as rq
from database.models import Rate, Subscribe
from utils.error_handling import error_handler
from config_data.config import Config, load_config

import logging
from datetime import datetime

config: Config = load_config()
router = Router()


# Персонал
@router.message(F.text == 'Мой тариф')
@error_handler
async def press_button_my_rate(message: Message, bot: Bot) -> None:
    """
    Проверка тарифа
    :param message:
    :param bot:
    :return:
    """
    logging.info(f'press_button_my_rate: {message.chat.id}')
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
            active_subscribe = True
    # если нет подписок или подписки не активны
    if not subscribes or not active_subscribe:
        await message.answer(text=f'У вас нет активных подписок')
    else:
        last_subscribe: Subscribe = subscribes[-1]
        rate_info: Rate = await rq.get_rate_id(rate_id=last_subscribe.rate_id)
        await message.answer(text=f'<b>Ваш тариф:</b> {rate_info.title_rate}\n'
                                  f'<b>Срок подписки:</b> {last_subscribe.date_completion}\n'
                                  f'<b>Количество вопросов:</b> {last_subscribe.count_question}/{rate_info.question_rate}',
                             reply_markup=kb.keyboard_send_question())
