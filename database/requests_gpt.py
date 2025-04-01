from database.models import async_session, QuestionGPT
from sqlalchemy import select, update
import logging
from datetime import datetime


""" QuestionGPT """


async def add_user_question_gpt(data: dict) -> None:
    """
    Добавление нового обращение к ИИ
    :param data:
    :return:
    """
    logging.info(f'add_user_question_gpt')
    async with async_session() as session:
        question_gpt = await session.scalar(select(QuestionGPT).where(QuestionGPT.tg_id_user == data["tg_id_user"]))
        if not question_gpt:
            question_gpt_ = QuestionGPT(**data)
            session.add(question_gpt_)
            await session.commit()


async def check_limit_free(tg_id: int) -> bool:
    """
    Уменьшение количества вопросов доступных к заданию ИИ
    :param tg_id:
    :return:
    """
    logging.info(f'add_user_question_gpt')
    async with async_session() as session:
        question_gpt: QuestionGPT = await session.scalar(select(QuestionGPT).where(QuestionGPT.tg_id_user == tg_id))
        if question_gpt.limit_free:
            limit_free_ = question_gpt.limit_free
            question_gpt.limit_free = limit_free_ - 1
            await session.commit()
            return True
        else:
            return False


async def check_date_payment(tg_id: int) -> bool:
    """
    Уменьшение количества вопросов доступных к заданию ИИ
    :param tg_id:
    :return:
    """
    logging.info(f'add_user_question_gpt')
    async with async_session() as session:
        question_gpt: QuestionGPT = await session.scalar(select(QuestionGPT).where(QuestionGPT.tg_id_user == tg_id))
        if question_gpt:
            current_date = datetime.now()
            if datetime.strptime(question_gpt.date_payment, "%d.%m.%Y") > current_date:
                return True
        else:
            return False


async def update_date_access_free_gpt(tg_id: int, date_payment: str) -> None:
    """
    Обновление даты свободного доступа к ИИ
    :param tg_id:
    :param date_payment:
    :return:
    """
    logging.info(f'add_user_question_gpt')
    async with async_session() as session:
        question_gpt = await session.scalar(select(QuestionGPT).where(QuestionGPT.tg_id_user == tg_id))
        if question_gpt:
            question_gpt.date_payment = date_payment
            await session.commit()


# async def update_limit_free_question_gpt() -> None:
#     """
#     Обновление количество вопросов для ИИ
#     :return:
#     """
#     logging.info(f'add_user_question_gpt')
#     async with async_session() as session:
#         stmt = (
#             update(QuestionGPT)
#             .values(limit_free=5)
#         )
#         await session.execute(stmt)
#         await session.commit()
#
#
# async def update_limit_pay_question_gpt() -> None:
#     """
#     Обновление количество вопросов для ИИ
#     :return:
#     """
#     logging.info(f'add_user_question_gpt')
#     async with async_session() as session:
#         stmt = (
#             update(QuestionGPT)
#             .values(limit_payment=5)
#         )
#         await session.execute(stmt)
#         await session.commit()






