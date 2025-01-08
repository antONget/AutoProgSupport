from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter, or_f
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, PreCheckoutQuery
from aiogram.fsm.context import FSMContext



from keyboards import start_keyboard as kb
from config_data.config import Config, load_config
from database import requests as rq
from database.models import User, Subscribe, Rate
from utils.error_handling import error_handler
from filter.admin_filter import check_super_admin

import logging
from datetime import datetime

router = Router()
config: Config = load_config()


@router.message(CommandStart())
@error_handler
async def process_start_command_user(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Пользовательский режим запускается если, пользователь ввел команду /start
     или если администратор ввел команду /user
    1. Добавляем пользователя в БД если его еще нет в ней
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_start_command_user: {message.chat.id}')
    await state.set_state(state=None)
    # добавление пользователя в БД если еще его там нет
    user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    if not user:
        if message.from_user.username:
            username = message.from_user.username
        else:
            username = "user_name"
        if await check_super_admin(telegram_id=message.from_user.id):
            role = rq.UserRole.admin
        else:
            role = rq.UserRole.user
        data_user = {"tg_id": message.from_user.id,
                     "username": username,
                     "role": role}
        await rq.add_user(data=data_user)
    # вывод клавиатуры в зависимости от роли пользователя
    user: User = await rq.get_user_by_id(tg_id=message.from_user.id)
    # пользователь
    if user.role == rq.UserRole.user:
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
            await message.answer(text=f'Приветственное сообщение! Описание того для чего предназначен этот бот',
                                 reply_markup=kb.keyboard_start(role=rq.UserRole.user))
        else:
            last_subscribe: Subscribe = subscribes[-1]
            rate_info: Rate = await rq.get_rate_id(rate_id=last_subscribe.rate_id)
            await message.answer(text=f'Добро пожаловать, {message.from_user.username}!\n\n'
                                      f'<b>Ваш тариф:</b> {rate_info.title_rate}\n'
                                      f'<b>Срок подписки:</b> {last_subscribe.date_completion}\n'
                                      f'<b>Количество вопросов:</b> {last_subscribe.count_question}/{rate_info.question_rate}',
                                 reply_markup=kb.keyboard_send_question())
    # партнер
    elif user.role == rq.UserRole.partner:
        await message.answer(text=f'Добро пожаловать! Вы являетесь ПАРТНЕРОМ проекта',
                             reply_markup=kb.keyboard_start(role=rq.UserRole.partner))

    # администратор
    elif user.role == rq.UserRole.admin:
        await message.answer(text=f'Добро пожаловать! Вы являетесь АДМИНИСТРАТОРОМ проекта',
                             reply_markup=kb.keyboard_start(role=rq.UserRole.admin))
