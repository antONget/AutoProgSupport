import asyncio

from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup

from utils.error_handling import error_handler
from config_data.config import Config, load_config
from services.openai.tg_assistant import send_message_to_openai


import logging


config: Config = load_config()
router = Router()
router.message.filter(F.chat.type == "private")


class GPT(StatesGroup):
    chatGPT = State()


@router.message(F.text == 'Спроси у ИИ')
@error_handler
async def press_button_gpt(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Открываем диалог с GPT
    :param message:
    :param bot:
    :param state:
    :return:
    """
    logging.info(f'press_button_gpt: {message.chat.id}')
    await message.answer(text=f'Задай свой вопрос chatGPT')
    await state.set_state(GPT.chatGPT)


@router.message(StateFilter(GPT.chatGPT))
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
        result = send_message_to_openai(user_id=message.from_user.id,
                                        user_input=message.text)
        await message.answer(text="⏳ Думаю...")
        await message.answer(text=result)



