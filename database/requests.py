from database.models import User, async_session, Subscribe, Rate, Question, Executor, Dialog, WithdrawalFunds,\
    Greeting, Partner, QuestionGPT
from sqlalchemy import select, or_, and_, update
import logging
from dataclasses import dataclass
from datetime import datetime


""" USER """


@dataclass
class UserRole:
    user = "user"
    partner = "partner"
    admin = "admin"


async def add_user(data: dict) -> None:
    """
    Добавление пользователя
    :param data:
    :return:
    """
    logging.info(f'add_user')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == data['tg_id']))
        if not user:
            session.add(User(**data))
            await session.commit()


async def set_user_role(tg_id: int, role: str) -> None:
    """
    Обновление роли пользователя
    :param tg_id:
    :param role:
    :return:
    """
    logging.info('set_user_role')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.role = role
            await session.commit()


async def set_offer_agreement(tg_id: int) -> None:
    """
    Обновление согласия с договором оферты
    :param tg_id:
    :return:
    """
    logging.info('set_user_role')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.offer_agreement = 1
            await session.commit()


async def set_user_fullname(tg_id: int, fullname: str) -> None:
    """
    Обновление роли пользователя
    :param tg_id:
    :param fullname:
    :return:
    """
    logging.info('set_user_fullname')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.fullname = fullname
            await session.commit()


async def update_user_balance(tg_id: int, change_balance: int) -> None:
    """
    Обновление баланса пользователя
    :param tg_id:
    :param change_balance:
    :return:
    """
    logging.info('set_user_fullname')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.balance += change_balance
            await session.commit()


async def get_user_by_id(tg_id: int) -> User:
    """
    Получение информации о пользователе по tg_id
    :param tg_id:
    :return:
    """
    logging.info('set_user_role')
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def get_users_role(role: str) -> list[User]:
    """
    Получение списка пользователей с заданной ролью
    :param role:
    :return:
    """
    logging.info('get_users_role')
    async with async_session() as session:
        users = await session.scalars(select(User).where(User.role == role))
        list_users = [user for user in users]
        return list_users


""" SUBSCRIBE """


async def add_subscribe(data: dict) -> None:
    """
    Добавление подписки пользователя
    :param data:
    :return:
    """
    logging.info(f'add_subscribe')
    async with async_session() as session:
        session.add(Subscribe(**data))
        await session.commit()


async def get_subscribes_user(tg_id: int) -> list[Subscribe]:
    """
    Получение списка подписок пользователя
    :param tg_id:
    :return:
    """
    logging.info('get_subscribes_user')
    async with async_session() as session:
        subscribes = await session.scalars(select(Subscribe).where(Subscribe.tg_id == tg_id))
        list_subscribes = [subscribe for subscribe in subscribes]
        return list_subscribes


async def set_subscribe_user(tg_id: int) -> None:
    """
    Увеличиваем количество заданных вопросов
    :param tg_id:
    :return:
    """
    logging.info('set_subscribe_user')
    async with async_session() as session:
        subscribes = await session.scalars(select(Subscribe).where(Subscribe.tg_id == tg_id))
        list_subscribes: list[Subscribe] = [subscribe for subscribe in subscribes]
        update_subscribe: Subscribe = list_subscribes[-1]
        update_subscribe.count_question += 1
        await session.commit()


""" RATE """


async def add_rate(data: dict) -> None:
    """
    Добавление тарифа
    :param data:
    :return:
    """
    logging.info(f'add_rate')
    async with async_session() as session:
        session.add(Rate(**data))
        await session.commit()


async def get_rate_id(rate_id: int) -> Rate:
    """
    Получение информации о тарифе
    :param rate_id:
    :return:
    """
    logging.info('get_rate_id')
    async with async_session() as session:
        return await session.scalar(select(Rate).where(Rate.id == rate_id))


async def get_list_rate() -> list[Rate]:
    """
    Получение списка тарифов
    :return:
    """
    logging.info('get_list_rate')
    async with async_session() as session:
        rates = await session.scalars(select(Rate))
        list_rates = [rate for rate in rates]
        return list_rates


async def rate_delete_id(rate_id: int) -> None:
    """
    Удаление тарифа
    :param rate_id:
    :return:
    """
    logging.info('get_rate_delete_id')
    async with async_session() as session:
        rate = await session.scalar(select(Rate).where(Rate.id == rate_id))
        if rate:
            await session.delete(rate)
            await session.commit()


""" QUESTION """


@dataclass
class QuestionStatus:
    create = "create"
    work = "work"
    cancel = "cancel"
    completed = "completed"
    delete = "delete"


async def add_question(data: dict) -> int:
    """
    Добавление вопроса пользователя и получение количества заданных вопросов
    :param data:
    :return:
    """
    logging.info(f'add_question')
    async with async_session() as session:
        new_question = Question(**data)
        session.add(new_question)
        await session.flush()
        id_ = new_question.id
        await session.commit()
        return id_


async def set_question_partner(question_id: int, partner_tg_id: int, message_id: int) -> None:
    """
    Добавление партнера в список рассылки вопроса
    :param question_id:
    :param partner_tg_id:
    :return:
    """
    logging.info('set_question_partner')
    async with async_session() as session:
        question = await session.scalar(select(Question).where(Question.id == question_id))
        partner_str = question.partner_list
        if partner_str == '':
            partner_str_ = f'{str(partner_tg_id)}!{message_id}'
        else:
            partner_list = partner_str.split(',')
            partner_list.append(f'{str(partner_tg_id)}!{message_id}')
            partner_str_ = ','.join(partner_list)
        question.partner_list = partner_str_
        await session.commit()


async def set_question_status(question_id: int, status: str) -> None:
    """
    Добавление партнера в список рассылки вопроса
    :param question_id:
    :param status:
    :return:
    """
    logging.info('set_question_status')
    async with async_session() as session:
        question = await session.scalar(select(Question).where(Question.id == question_id))
        question.status = status
        await session.commit()


async def set_question_completed(question_id: int, partner: int) -> None:
    """
    Добавление партнера в список рассылки вопроса
    :param question_id:
    :param partner:
    :return:
    """
    logging.info('set_question_status')
    async with async_session() as session:
        question = await session.scalar(select(Question).where(Question.id == question_id))
        question.partner_solution = partner
        current_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        question.date_solution = current_date
        await session.commit()


async def set_question_quality(question_id: int, quality: int) -> None:
    """
    Обновление качества ответа
    :param question_id:
    :param quality:
    :return:
    """
    logging.info('set_question_quality')
    async with async_session() as session:
        question = await session.scalar(select(Question).where(Question.id == question_id))
        question.quality = quality
        await session.commit()


async def set_question_data_solution(question_id: int, data_solution: str) -> None:
    """
    Обновление качества ответа
    :param question_id:
    :param data_solution:
    :return:
    """
    logging.info(f'set_question_data_solution {question_id} {data_solution}')
    async with async_session() as session:
        question = await session.scalar(select(Question).where(Question.id == question_id))
        question.date_solution = data_solution
        await session.commit()


async def set_question_comment(question_id: int, comment: str) -> None:
    """
    Обновление комментария к вопросу
    :param question_id:
    :param comment:
    :return:
    """
    logging.info('set_question_comment')
    async with async_session() as session:
        question = await session.scalar(select(Question).where(Question.id == question_id))
        question.comment = comment
        await session.commit()


async def set_question_executor(question_id: int, executor: int) -> None:
    """
    Устанавливаем исполнителя для решения вопроса
    :param question_id:
    :param executor:
    :return:
    """
    logging.info('set_question_executor')
    async with async_session() as session:
        question = await session.scalar(select(Question).where(Question.id == question_id))
        question.partner_solution = executor
        await session.commit()


async def get_question_id(question_id: int) -> Question:
    """
    Получаем вопрос по его id
    :param question_id:
    :return:
    """
    logging.info('get_question_id')
    async with async_session() as session:
        return await session.scalar(select(Question).where(Question.id == question_id))


async def delete_question_id(question_id: int) -> None:
    """
    Получаем вопрос по его id
    :param question_id:
    :return:
    """
    logging.info('get_question_id')
    async with async_session() as session:
        question = await session.scalar(select(Question).where(Question.id == question_id))
        if question:
            await session.delete(question)


async def get_questions_tg_id(partner_solution: int) -> list[Question]:
    """
    Получаем список завершенных вопросов для конкретного партнера
    :param partner_solution:
    :return:
    """
    logging.info('get_question_id')
    async with async_session() as session:
        questions = await session.scalars(select(Question).where(Question.partner_solution == partner_solution,
                                                                 Question.status == QuestionStatus.completed))
        return [question for question in questions]


async def get_questions() -> list[Question]:
    """
    Получаем все вопросы
    :return:
    """
    logging.info('get_question_id')
    async with async_session() as session:
        return await session.scalars(select(Question))


async def get_questions_cancel_create() -> list[Question]:
    """
    Получаем все вопросы
    :return:
    """
    logging.info('get_questions_cancel_create')
    async with async_session() as session:
        questions = await session.scalars(select(Question).where(or_(Question.status == QuestionStatus.create,
                                                                     Question.status == QuestionStatus.cancel)))
        list_question = [question for question in questions]
        return list_question


""" EXECUTOR """


@dataclass
class ExecutorStatus:
    create = "create"
    work = "work"
    cancel = "cancel"
    completed = "completed"



async def add_executor(data: dict) -> None:
    """
    Добавление исполнителя в рассылку
    :param data:
    :return:
    """
    logging.info(f'add_question')
    async with async_session() as session:
        new_executor = Executor(**data)
        session.add(new_executor)
        await session.commit()


async def set_status_executor(question_id: int, tg_id: int, status: str) -> None:
    """
    Обновление статуса исполнителя
    :param question_id:
    :param tg_id:
    :param status:
    :return:
    """
    logging.info('set_question_quality')
    async with async_session() as session:
        executor = await session.scalar(select(Executor).where(Executor.id_question == question_id,
                                                               Executor.tg_id == tg_id))
        if executor:
            executor.status = status
            await session.commit()


async def set_executor_comment_cancel(question_id: int, tg_id: int, comment_cancel: str) -> None:
    """
    Обновление комментария отказа от вопроса
    :param question_id:
    :param tg_id:
    :param comment_cancel:
    :return:
    """
    logging.info('set_executor_comment_cancel')
    async with async_session() as session:
        executor = await session.scalar(select(Executor).where(Executor.id_question == question_id,
                                                               Executor.tg_id == tg_id))
        if executor:
            executor.comment_cancel = comment_cancel
            await session.commit()


async def set_cost_executor(question_id: int, tg_id: int, cost: int) -> None:
    """
    Обновление стоимости выполнения заявки партнером
    :param question_id:
    :param tg_id:
    :param cost:
    :return:
    """
    logging.info('set_question_quality')
    async with async_session() as session:
        executor = await session.scalar(select(Executor).where(Executor.id_question == question_id,
                                                               Executor.tg_id == tg_id))
        if executor:
            executor.cost = cost
            await session.commit()


async def update_cost_executor(question_id: int, tg_id: int, cost: int) -> None:
    """
    Обновление стоимости выполнения заявки партнером
    :param question_id:
    :param tg_id:
    :param cost:
    :return:
    """
    logging.info('set_question_quality')
    async with async_session() as session:
        executor = await session.scalar(select(Executor).where(Executor.id_question == question_id,
                                                               Executor.tg_id == tg_id))
        if executor:
            executor.cost += cost
            await session.commit()


async def set_message_id_cost_executor(question_id: int, tg_id: int, message_id_cost: int) -> None:
    """
    Обновление номера сообщения с предложением стоимости решения отправленное пользователю
    :param question_id:
    :param tg_id:
    :param message_id_cost:
    :return:
    """
    logging.info('set_message_id_cost_executor')
    async with async_session() as session:
        executor = await session.scalar(select(Executor).where(Executor.id_question == question_id,
                                                               Executor.tg_id == tg_id))
        if executor:
            executor.message_id_cost = message_id_cost
            await session.commit()


async def set_message_id_executor(question_id: int, tg_id: int, message_id: int) -> None:
    """
    Обновление сообщения с вопросом после ответа о стоимости у партнера
    :param question_id:
    :param tg_id:
    :param message_id:
    :return:
    """
    logging.info('set_message_id_executor')
    async with async_session() as session:
        executor = await session.scalar(select(Executor).where(Executor.id_question == question_id,
                                                               Executor.tg_id == tg_id))
        if executor:
            executor.message_id = message_id
            await session.commit()


async def get_executor(question_id: int, tg_id: int) -> Executor:
    """
    Получаем исполнителя по номеру рассылки вопроса
    :param question_id:
    :param tg_id:
    :return:
    """
    logging.info('set_question_quality')
    async with async_session() as session:
        return await session.scalar(select(Executor).where(Executor.id_question == question_id,
                                                           Executor.tg_id == tg_id))


async def get_executor_not(question_id: int, tg_id: int) -> list[Executor]:
    """
    Получаем исполнителей которых не выбрали для решения вопроса
    :param question_id:
    :param tg_id:
    :return:
    """
    logging.info('set_question_quality')
    async with async_session() as session:
        return await session.scalars(select(Executor).where(Executor.id_question == question_id,
                                                            Executor.tg_id != tg_id))


async def get_executors(question_id: int) -> list[Executor]:
    """
    Получаем исполнителей которым отправлен вопрос
    :param question_id:
    :return:
    """
    logging.info('set_question_quality')
    async with async_session() as session:
        return await session.scalars(select(Executor).where(Executor.id_question == question_id))


async def del_executor(question_id: int, tg_id: int) -> None:
    """
    Удаляем всех пользователей из списка рассылки вопроса
    :param question_id:
    :param tg_id:
    :return:
    """
    logging.info('set_question_quality')
    async with async_session() as session:
        executor = await session.scalar(select(Executor).where(Executor.id_question == question_id,
                                                               Executor.tg_id == tg_id))
        if executor:
            await session.delete(executor)
            await session.commit()


""" DIALOG """


@dataclass
class StatusDialog:
    active = 'active'
    completed = 'completed'


async def add_dialog(data: dict) -> int:
    """
    Добавление нового диалога между пользователем и партнером для обсуждения вопроса
    :param data:
    :return:
    """
    logging.info(f'add_dialog')
    async with async_session() as session:
        new_dialog = Dialog(**data)
        session.add(new_dialog)
        await session.flush()
        id_ = new_dialog.id
        await session.commit()
        return id_


async def get_dialog_active_tg_id(tg_id: int) -> Dialog:
    """
    Получаем активный диалог пользователя
    :param tg_id:
    :return:
    """
    logging.info('get_dialog_active_tg_id')
    async with async_session() as session:
        return await session.scalar(select(Dialog).filter(and_(or_(Dialog.tg_id_user == tg_id,
                                                                   Dialog.tg_id_partner == tg_id),
                                                          Dialog.status == StatusDialog.active)))


async def set_dialog_active_tg_id_message(id_dialog: int, message_thread_id: int) -> None:
    """
    Обновляем номер топика в активном диалоге
    :param id_dialog:
    :param message_thread_id
    :return:
    """
    logging.info('get_dialog_active_tg_id')
    async with async_session() as session:
        dialog = await session.scalar(select(Dialog).filter(Dialog.id == id_dialog))
        if dialog:
            dialog.message_thread_id = message_thread_id
            await session.commit()


async def set_dialog_completed_tg_id(tg_id: int) -> None:
    """
    Закрываем диалог
    :param tg_id:
    :return:
    """
    logging.info('set_dialog_completed_tg_id')
    async with async_session() as session:
        dialog = await session.scalar(select(Dialog).filter(and_(or_(Dialog.tg_id_user == tg_id,
                                                                     Dialog.tg_id_partner == tg_id),
                                                            Dialog.status == StatusDialog.active)))
        if dialog:
            dialog.status = StatusDialog.completed
            await session.commit()


""" WithdrawalFunds """


@dataclass
class StatusWithdrawalFunds:
    create = 'create'
    completed = 'confirm'
    cancel = 'cancel'


async def add_withdrawal_funds(data: dict) -> int:
    """
    Добавление нового запроса на вывод средств
    :param data:
    :return:
    """
    logging.info(f'add_withdrawal_funds')
    async with async_session() as session:
        new_withdrawal_funds = WithdrawalFunds(**data)
        session.add(new_withdrawal_funds)
        await session.flush()
        id_ = new_withdrawal_funds.id
        await session.commit()
        return id_


async def set_withdrawal_funds_status(id_: int, status: str, balance_after: int, tg_id_admin: int) -> None:
    """
    Обновляем поля запроса на вывод средств
    :param id_:
    :param status:
    :param balance_after:
    :param tg_id_admin:
    :return:
    """
    logging.info('set_dialog_completed_tg_id')
    async with async_session() as session:
        withdrawal_funds: WithdrawalFunds = await session.scalar(select(WithdrawalFunds).filter(WithdrawalFunds.id == id_))
        if withdrawal_funds:
            withdrawal_funds.status = status
            current_date = datetime.now().strftime('%d.%m.%Y %H:%M')
            withdrawal_funds.data_confirm = current_date
            withdrawal_funds.balance_after = balance_after
            withdrawal_funds.tg_id_admin = tg_id_admin
            await session.commit()


async def get_withdrawal_funds_id(id_: int) -> WithdrawalFunds:
    """
    Получаем запрос на списание средств
    :param id_:
    :return:
    """
    logging.info('set_dialog_completed_tg_id')
    async with async_session() as session:
        withdrawal_fund: WithdrawalFunds = await session.scalar(select(WithdrawalFunds).
                                                                filter(WithdrawalFunds.id == id_))
        if withdrawal_fund:
            return withdrawal_fund


""" GREETING """


async def get_greeting() -> Greeting:
    """
    Получаем приветствие
    :return:
    """
    logging.info('get_greeting')
    async with async_session() as session:
        return await session.scalar(select(Greeting))


async def set_greeting(greet_text: str) -> None:
    """
    Обновление приветствия
    :return:
    """
    logging.info('set_dialog_completed_tg_id')
    async with async_session() as session:
        greeting: Greeting = await session.scalar(select(Greeting))
        if greeting:
            greeting.greet_text = greet_text
            await session.commit()


""" PARTNERS """


async def add_partner(data: dict) -> None:
    """
    Добавление нового партнера
    :param data:
    :return:
    """
    logging.info(f'add_withdrawal_funds')
    async with async_session() as session:
        partner = await session.scalar(select(Partner).where(Partner.tg_id_partner == data["tg_id_partner"]))
        if not partner:
            partner = Partner(**data)
            session.add(partner)
            await session.commit()


async def get_partners() -> list[Partner]:
    """
    Получаем список партнеров
    :return:
    """
    logging.info('get_partners')
    async with async_session() as session:
        partners = await session.scalars(select(Partner))
        list_partners = [partner.tg_id_partner for partner in partners]
        return list_partners


async def del_partner(tg_id: int) -> None:
    """
    Удаление партнера
    :param tg_id:
    :return:
    """
    logging.info(f'add_withdrawal_funds')
    async with async_session() as session:
        partner = await session.scalar(select(Partner).where(Partner.tg_id_partner == tg_id))
        await session.delete(partner)
        await session.commit()


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


async def update_limit_free_question_gpt() -> None:
    """
    Обновление количество вопросов для ИИ
    :return:
    """
    logging.info(f'add_user_question_gpt')
    async with async_session() as session:
        stmt = (
            update(QuestionGPT)
            .values(limit_free=5)
        )
        await session.execute(stmt)
        await session.commit()


async def update_limit_pay_question_gpt() -> None:
    """
    Обновление количество вопросов для ИИ
    :return:
    """
    logging.info(f'add_user_question_gpt')
    async with async_session() as session:
        stmt = (
            update(QuestionGPT)
            .values(limit_payment=5)
        )
        await session.execute(stmt)
        await session.commit()


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
            if question_gpt.date_payment == 'none':
                return False
            else:
                current_date = datetime.now()
                if datetime.strptime(question_gpt.date_payment, "%d.%m.%Y") > current_date:
                    return True
        else:
            return False