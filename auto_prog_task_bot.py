from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config_data.config import Config, load_config
from handlers import error, other_handlers, start_handler
from handlers.admin import handler_edit_list_personal, handler_edit_list_rate, handler_withdrawal_funds, \
    handler_questions_delete
from handlers.partner import handler_partner_answer, handler_dialog_partner, handler_report, handler_account, \
    handler_send_receipt, handler_cancel_question, handler_questions
from handlers.user import handler_rates, handler_user_quality_answer, handler_send_question, handler_ask_master,\
    handler_select_partner, handler_balance, handler_FAQ, handler_assistant_gpt
from notify_admins import on_startup_notify
from database.models import async_main
from database.requests import update_limit_free_question_gpt
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import logging

logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    """
    Основной файл для запуска
    :return:
    """
    await async_main()
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        filename="py_log.log",
        filemode='w',
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    # scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    # # каждый день
    # scheduler.add_job(update_limit_free_question_gpt, 'cron', hour="*")
    # scheduler.start()
    await on_startup_notify(bot=bot)
    # Регистрируем router в диспетчере
    dp.include_router(error.router)
    dp.include_router(start_handler.router)
    dp.include_routers(handler_edit_list_personal.router,
                       handler_edit_list_rate.router,
                       handler_withdrawal_funds.router,
                       handler_questions_delete.router)
    dp.include_routers(handler_partner_answer.router,
                       handler_dialog_partner.router,
                       handler_report.router,
                       handler_account.router,
                       handler_send_receipt.router,
                       handler_cancel_question.router,
                       handler_questions.router)
    dp.include_routers(handler_FAQ.router,
                       handler_assistant_gpt.router,
                       handler_rates.router,
                       handler_balance.router,
                       handler_ask_master.router,
                       handler_send_question.router,
                       handler_user_quality_answer.router,
                       handler_select_partner.router,
                       )
    dp.include_router(other_handlers.router)

    # Пропускаем накопившиеся update и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
