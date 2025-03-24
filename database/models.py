from sqlalchemy import String, Integer, DateTime, BigInteger, Boolean, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


engine = create_async_engine(url='sqlite+aiosqlite:///database/db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'Users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String, nullable=True)
    fullname: Mapped[str] = mapped_column(String, default='none')
    balance: Mapped[int] = mapped_column(Integer, default=0)
    role: Mapped[str] = mapped_column(String, default='user')
    offer_agreement: Mapped[int] = mapped_column(Integer, default=0)


class Subscribe(Base):
    __tablename__ = 'Subscribes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    rate_id: Mapped[int] = mapped_column(Integer)
    date_start: Mapped[str] = mapped_column(String)
    date_completion: Mapped[str] = mapped_column(String)
    count_question: Mapped[int] = mapped_column(Integer, default=0)


class Rate(Base):
    __tablename__ = 'Rates'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title_rate: Mapped[str] = mapped_column(String)
    amount_rate: Mapped[int] = mapped_column(Integer)
    duration_rate: Mapped[int] = mapped_column(Integer)
    question_rate: Mapped[int] = mapped_column(Integer)


class Question(Base):
    __tablename__ = 'Questions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    description: Mapped[str] = mapped_column(String)
    content_ids: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    date_solution: Mapped[str] = mapped_column(String, default='')
    partner_solution: Mapped[int] = mapped_column(BigInteger, default=0)
    quality: Mapped[int] = mapped_column(BigInteger, default=-1)
    comment: Mapped[str] = mapped_column(String, default='')


class Executor(Base):
    __tablename__ = 'executors'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    message_id: Mapped[int] = mapped_column(Integer)
    message_id_cost: Mapped[int] = mapped_column(Integer, default=0)
    id_question: Mapped[int] = mapped_column(Integer)
    cost: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String)
    comment_cancel: Mapped[str] = mapped_column(String, default='')


class Dialog(Base):
    __tablename__ = 'dialogs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id_user: Mapped[int] = mapped_column(BigInteger)
    tg_id_partner: Mapped[int] = mapped_column(BigInteger)
    id_question: Mapped[int] = mapped_column(Integer)
    message_thread_id: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String)


class WithdrawalFunds(Base):
    __tablename__ = 'withdrawal_funds'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id_partner: Mapped[int] = mapped_column(BigInteger)
    summ_withdrawal_funds: Mapped[int] = mapped_column(Integer)
    data_withdrawal: Mapped[str] = mapped_column(String)
    balance_before: Mapped[int] = mapped_column(Integer)
    requisites: Mapped[str] = mapped_column(String)
    data_confirm: Mapped[str] = mapped_column(String, default='')
    balance_after: Mapped[int] = mapped_column(Integer, default=0)
    tg_id_admin: Mapped[int] = mapped_column(BigInteger, default=0)
    status: Mapped[str] = mapped_column(String, default='create')


class Greeting(Base):
    __tablename__ = 'greeting'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    greet_text: Mapped[str] = mapped_column(String)


class Partner(Base):
    __tablename__ = 'partners'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id_partner: Mapped[int] = mapped_column(BigInteger)


class QuestionGPT(Base):
    __tablename__ = 'questions_gpt'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id_user: Mapped[int] = mapped_column(BigInteger)
    limit_free: Mapped[int] = mapped_column(Integer, default=5)
    limit_payment: Mapped[int] = mapped_column(Integer, default=0)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


