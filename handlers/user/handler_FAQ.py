from aiogram import F, Router, Bot
from aiogram.types import Message

from utils.error_handling import error_handler
from config_data.config import Config, load_config

import logging


config: Config = load_config()
router = Router()
router.message.filter(F.chat.type == "private")


@router.message(F.text == 'FAQ')
@error_handler
async def press_button_FAQ(message: Message, bot: Bot) -> None:
    """
    Выбор тарифа для подписки
    :param message:
    :param bot:
    :return:
    """
    logging.info(f'press_button_FAQ: {message.chat.id}')
    await message.answer(text=f'В этом разделе вы можете ознакомиться с часто возникающими вопросами (В разработке)')

