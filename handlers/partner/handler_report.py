from aiogram.types import CallbackQuery, Message
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import StateFilter
from aiogram.filters.callback_data import CallbackData
import aiogram_calendar
from aiogram_calendar import get_user_locale


from datetime import datetime, timedelta, date
from filter.admin_filter import check_super_admin
from database import requests as rq
from database.models import Question, Executor, User
import logging

router = Router()


class StateReport(StatesGroup):
    start_period = State()
    finish_period = State()



# календарь
@router.message(F.text == 'Отчет')
async def process_buttons_press_report(message: Message, state: FSMContext):
    """
    Паздел отчет
    :param message:
    :param state:
    :return:
    """
    logging.info('process_buttons_press_report')
    await state.set_state(state=None)
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2015, 1, 1), datetime(2050, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%d/%m/%Y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await message.answer(
        "Выберите начало периода получения отчета",
        reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
    )
    await state.set_state(StateReport.start_period)


async def process_buttons_press_finish(callback: CallbackQuery, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2015, 1, 1), datetime(2050, 12, 31))
    # получаем текущую дату
    current_date = datetime.now()
    # преобразуем ее в строку
    date1 = current_date.strftime('%d/%m/%Y')
    # преобразуем дату в список
    list_date1 = date1.split('/')
    await callback.message.edit_text(
        "Выберите конец периода получения отчета",
        reply_markup=await calendar.start_calendar(year=int(list_date1[2]), month=int(list_date1[1]))
    )
    await callback.answer()
    await state.set_state(StateReport.finish_period)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(StateReport.start_period))
async def process_simple_calendar_start(callback_query: CallbackQuery, callback_data: CallbackData,
                                        state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date_start = await calendar.process_selection(callback_query, callback_data)
    if selected:
        # await callback_query.message.edit_text(
        #     f'Начало периода {date.strftime("%d-%m-%Y")}')
        await state.update_data(start_period=date_start)
        await process_buttons_press_finish(callback_query, state=state)


@router.callback_query(aiogram_calendar.SimpleCalendarCallback.filter(), StateFilter(StateReport.finish_period))
async def process_simple_calendar_finish(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = aiogram_calendar.SimpleCalendar(show_alerts=True)
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2030, 12, 31))
    selected, date_finish = await calendar.process_selection(callback, callback_data)
    if selected:
        await state.update_data(finish_period=date_finish)
        await state.set_state(state=None)
        if await check_super_admin(telegram_id=callback.from_user.id):
            questions: list[Question] = await rq.get_questions()
        else:
            questions: list[Question] = await rq.get_question_tg_id(partner_solution=callback.from_user.id)
        if questions:
            list_questions: list = []
            data = await state.get_data()
            start_period = data['start_period']
            text = ''
            total = 0
            for question in questions:
                if question.date_solution:
                    date_question = datetime(year=int(question.date_solution.split('-')[2].split()[0]),
                                             month=int(question.date_solution.split('-')[1]),
                                             day=int(question.date_solution.split('-')[0]))
                    if start_period <= date_question <= date_finish:
                        list_questions.append(question)
                        executor: Executor = await rq.get_executor(question_id=question.id,
                                                                   tg_id=question.partner_solution)
                        info_user: User =await rq.get_user_by_id(tg_id=question.tg_id)
                        info_partner: User = await rq.get_user_by_id(tg_id=question.partner_solution)
                        text += f'Специалист #_{info_partner.id} оказал услугу № {question.id } пользователю #_{question.id}' \
                                f' на сумму {executor.cost}\n'
                        total += executor.cost
            if text == '':
                await callback.message.answer(text='Нет оказанных услуг за выбранный рериод')
                return
            text += f'ИТОГО: {total}'
            await callback.message.answer(text=text)
        else:
            await callback.message.answer(text=f'В выбранный период нет оказанных услуг')