from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, or_f

import keyboards.user.keyboards_rate as kb
from keyboards.user.keyboards_my_rate import keyboard_ask_typy, keyboard_ask_master, keyboard_send
import database.requests as rq
from database.models import Rate, Subscribe, Dialog
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


async def check_subscribe(message: Message, tg_id: int):
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
                                  f'<b>Количество вопросов:</b> {last_subscribe.count_question}/'
                                  f'{rate_info.question_rate}\n\n'
                                  f'Выберите кому вы бы хотели адресовать вопрос',
                             reply_markup=keyboard_ask_typy())


# Персонал
@router.message(F.text == 'Задать вопрос')
@error_handler
async def press_button_ask_question(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Проверка тарифа
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'press_button_ask_question: {message.chat.id}')
    info_dialog: Dialog = await rq.get_dialog_active_tg_id(tg_id=message.from_user.id)
    if info_dialog:
        await message.answer(text=f'У вас есть не закрытый диалог для решения вопроса №{info_dialog.id_question}, '
                                  f'для его закрытия введите команду /close_dialog')
        return
    await message.answer(text=f'В этом разделе вы можете задать свой вопрос',
                         reply_markup=kb.keyboard_main_menu())
    await message.answer(text=f'Выберите кому вы бы хотели адресовать вопрос',
                         reply_markup=keyboard_ask_typy())


@router.callback_query(F.data.startswith('ask'))
async def get_type_ask(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Получаем кому следует адресовать вопрос
    :param callback: ask_artificial_intelligence, ask_master
    :param state:
    :param bot:
    :return:
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
        await rq.add_user_question_gpt(data={"tg_id_user": callback.from_user.id})
    await callback.answer()


@router.message(F.text == 'Задать вопрос специалисту')
@error_handler
async def ask_question_master(message: Message, state: FSMContext, bot: Bot):
    """
    Переключаемся для задания вопроса специалисту
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'ask_question_master {message.chat.id}')
    await state.set_state(QuestionState.question)
    await state.update_data(content='')
    await message.answer(text='Пришлите описание вашей проблемы, можете добавить фото или файл 📎 .',
                         reply_markup=kb.keyboard_main_menu())
    await state.update_data(task='')


@router.message(StateFilter(QuestionState.question), or_f(F.photo, F.text, F.document))
@error_handler
async def request_content_photo_text(message: Message, state: FSMContext, bot: Bot):
    """
    Получаем от пользователя контент для публикации
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'request_content_photo_text {message.chat.id}')
    # await asyncio.sleep(random.random())
    # await state.update_data(content=[])
    # await state.update_data(count=[])
    # await state.update_data(task='')
    data = await state.get_data()
    # list_content = data.get('content', [])
    # count = data.get('count', [])
    content = data['content']
    task = data['task']
    if message.text:
        # data = await state.get_data()
        if task == '':
            task = message.html_text
        else:
            task += f'\n + {message.html_text}'
        await state.update_data(task=task)
        # await message.edit_text(text=f'📎 Прикрепите фото или файл.\n'
        #                              f'Добавить еще материал или отправить?',
        #                         reply_markup=kb.keyboard_send())

    elif message.photo:
        content = f'photo!{message.photo[-1].file_id}'
        task = data['task']
        if message.caption:
            if task == '':
                task = message.caption
            else:
                task += f'\n{message.caption}'
            await state.update_data(task=task)
        await state.update_data(content=content)
    elif message.document:
        logging.info(f'{message.document.file_id}')
        content = f'file!{message.document.file_id}'
        task = data['task']
        if message.caption:
            if task == '':
                task = message.caption
            else:
                task += f'\n{message.caption}'
            await state.update_data(task=task)
        await state.update_data(content=content)
    # await state.update_data(count=count)
    await state.set_state(state=None)
    if content == '':
        await message.answer(text=f'{task}\n\n'
                                  f'📎 Прикрепите фото или файл.\n'
                                  f'Добавить еще материал или отправить?',
                             reply_markup=keyboard_send())
    else:
        typy_file = content.split('!')[0]
        if typy_file == 'photo':
            await message.answer_photo(photo=content.split('!')[1],
                                       caption=f'{task}\n\n'
                                               f'📎 Прикрепите фото или файл.\n'
                                               f'Добавить еще материал или отправить?',
                                       reply_markup=keyboard_send())
        elif typy_file == 'file':
            await message.answer_document(document=content.split('!')[1],
                                          caption=f'{task}\n\n'
                                                  f'📎 Прикрепите фото или файл.\n'
                                                  f'Добавить еще материал или отправить?',
                                          reply_markup=keyboard_send())


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
        if await rq.update_user_question_gpt(tg_id=message.from_user.id):
            await message.answer(text="⏳ Думаю...")
            result = send_message_to_openai(user_id=message.from_user.id,
                                            user_input=message.text)
            await message.answer(text=result)
        else:
            await message.answer(text='Вы исчерпали лимит бесплатных вопросов для ИИ,'
                                      ' вы можете приобрести еще доступ к ИИ или обратиться к специалистам')

