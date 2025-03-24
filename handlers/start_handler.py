from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter, or_f
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from keyboards import start_keyboard as kb
from config_data.config import Config, load_config
from database import requests as rq
from database.models import User, Subscribe, Rate, Dialog, Greeting, Partner
from utils.error_handling import error_handler
from filter.admin_filter import check_super_admin, IsSuperAdmin
from filter.user_filter import check_role

import logging
from datetime import datetime

router = Router()
config: Config = load_config()


class StateGreet(StatesGroup):
    greet = State()


async def check_subscribe_user(message: Message, tg_id: int, greet_text: str):
    """
    Функция для проверки подписки
    :return:
    """
    # проверка на наличие активной подписки
    subscribes: list[Subscribe] = await rq.get_subscribes_user(tg_id=tg_id)
    active_subscribe = False
    if subscribes:
        last_subscribe: Subscribe = subscribes[-1]
        date_format = '%d-%m-%Y %H:%M'
        current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        delta_time = (datetime.strptime(current_date, date_format) -
                      datetime.strptime(last_subscribe.date_completion, date_format))
        rate: Rate = await rq.get_rate_id(rate_id=last_subscribe.rate_id)
        if rate:
            if delta_time.days < rate.duration_rate:
                rate: Rate = await rq.get_rate_id(rate_id=last_subscribe.rate_id)
                if last_subscribe.count_question < rate.question_rate:
                    active_subscribe = True
        else:
            active_subscribe = False
    # если нет подписок или подписки не активны
    if not subscribes or not active_subscribe:
        await message.answer(text=f'{greet_text}',
                             reply_markup=await kb.keyboard_start(role=rq.UserRole.user,
                                                                  tg_id=message.from_user.id))
    else:
        last_subscribe: Subscribe = subscribes[-1]
        rate_info: Rate = await rq.get_rate_id(rate_id=last_subscribe.rate_id)
        await message.answer(text=f'Добро пожаловать, {message.from_user.username}!\n\n'
                                  f'<b>Ваш тариф:</b> {rate_info.title_rate}\n'
                                  f'<b>Срок подписки:</b> {last_subscribe.date_completion}\n'
                                  f'<b>Количество вопросов:</b> {last_subscribe.count_question}/'
                                  f'{rate_info.question_rate}',
                             reply_markup=await kb.keyboard_start(role=rq.UserRole.user,
                                                                  tg_id=message.from_user.id))


@router.message(CommandStart())
@router.message(F.text == 'Главное меню')
@error_handler
async def process_start_command_user(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Обработки запуска бота или ввода команды /start
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'process_start_command_user: {message.chat.id}')
    await state.set_state(state=None)
    info_dialog: Dialog = await rq.get_dialog_active_tg_id(tg_id=message.from_user.id)
    if info_dialog:
        await message.answer(text=f'У вас есть не закрытый диалог для решения вопроса №{info_dialog.id_question}, '
                                  f'для его закрытия введите команду /close_dialog')
        return
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
    if not user.offer_agreement:
        await message.answer(text='🔒 Согласие с договором оферты\n\n'
                                  'Перед тем как продолжить, пожалуйста, ознакомьтесь с условиями нашего договора'
                                  ' оферты. Вы можете <a href="https://telegra.ph/DOGOVOR-OFERTY-02-16-3">'
                                  'просмотреть договор.</a>\n\n'
                                  'Если вы согласны с условиями, нажмите кнопку «Согласен»,'
                                  ' чтобы подтвердить свое согласие и продолжить использование наших услуг.',
                             reply_markup=kb.keyboard_offer_agreement())
        return
    greet: Greeting = await rq.get_greeting()
    # пользователь
    if user.role == rq.UserRole.user:
        await message.answer(text=f'{greet.greet_text}',
                             reply_markup=await kb.keyboard_start(role=rq.UserRole.user,
                                                                  tg_id=message.from_user.id))
    # партнер
    elif user.role == rq.UserRole.partner:
        await message.answer(text=f'{greet.greet_text}\n\nВы являетесь ПАРТНЕРОМ проекта',
                             reply_markup=await kb.keyboard_start(role=rq.UserRole.partner,
                                                                  tg_id=message.from_user.id))

    # администратор
    elif user.role == rq.UserRole.admin:
        await message.answer(text=f'{greet.greet_text}\n\nВы являетесь АДМИНИСТРАТОРОМ проекта',
                             reply_markup=await kb.keyboard_start(role=rq.UserRole.admin,
                                                                  tg_id=message.from_user.id))


@router.callback_query(F.data == 'change_role_admin')
@router.callback_query(F.data == 'change_role_partner')
@error_handler
async def change_role_admin(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Смена роли администратором
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_role_admin')
    list_partner: list[Partner] = await rq.get_partners()
    if await check_super_admin(telegram_id=callback.from_user.id):
        await callback.message.edit_text(text=f'Какую роль установить?',
                                         reply_markup=kb.keyboard_select_role_admin())
    elif callback.from_user.id in list_partner:
        await callback.message.edit_text(text=f'Какую роль установить?',
                                         reply_markup=kb.keyboard_select_role_partner())


@router.callback_query(F.data.startswith('select_role_'))
@error_handler
async def change_role_admin_select_role(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Смена роли администратором на выбранную
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_role_admin_select_role')
    await callback.message.delete()
    select_role = callback.data.split('_')[-1]
    await rq.set_user_role(tg_id=callback.from_user.id, role=select_role)
    await callback.message.answer(text=f'Роль {select_role.upper()} успешно установлена',
                                  reply_markup=await kb.keyboard_start(role=select_role, tg_id=callback.from_user.id))
    await process_start_command_user(message=callback.message, state=state, bot=bot)


@router.message(F.text == '/change_greeting', IsSuperAdmin())
@error_handler
async def change_greeting(message: Message, state: FSMContext, bot: Bot):
    """
    Обновление приветствия
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('change_greeting')
    await message.answer(text='Пришлите новое приветствие или пришлите /cancel')
    await state.set_state(StateGreet.greet)


@router.message(F.text, StateFilter(StateGreet.greet))
@error_handler
async def get_greet(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем новое приветствие
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info('get_greet')
    greeting = message.html_text
    await state.set_state(state=None)
    if greeting == '/cancel':
        await message.answer(text='Обновление приветствия отменено')
        return
    else:
        await rq.set_greeting(greet_text=greeting)
        await message.answer(text='Приветствие обновлено')


@router.callback_query(F.data.startswith('offer_agreement_'))
@error_handler
async def offer_agreement_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Договор оферты
    :param callback:
    :param state:
    :param bot:
    :return:
    """
    logging.info('offer_agreement_confirm')
    action = callback.data.split('_')[-1]
    # согласие с договором оферты
    if action == 'confirm':
        # устанавливаем что пользователь согласился с договором
        await rq.set_offer_agreement(tg_id=callback.from_user.id)
        # получаем приветственное сообщение
        greet: Greeting = await rq.get_greeting()
        # получаем информацию о пользователе
        user: User = await rq.get_user_by_id(tg_id=callback.from_user.id)
        # если пользователь, имеет роль пользователь
        if user.role == rq.UserRole.user:
            await callback.message.answer(text=f'{greet.greet_text}',
                                          reply_markup=await kb.keyboard_start(role=rq.UserRole.user,
                                                                               tg_id=callback.from_user.id))
        # партнер
        elif user.role == rq.UserRole.partner:
            await callback.message.answer(text=f'{greet.greet_text}\n\nВы являетесь ПАРТНЕРОМ проекта',
                                          reply_markup=await kb.keyboard_start(role=rq.UserRole.partner,
                                                                               tg_id=callback.from_user.id))

        # администратор
        elif user.role == rq.UserRole.admin:
            await callback.message.answer(text=f'{greet.greet_text}\n\nВы являетесь АДМИНИСТРАТОРОМ проекта',
                                          reply_markup=await kb.keyboard_start(role=rq.UserRole.admin,
                                                                               tg_id=callback.from_user.id))
    await callback.answer()
