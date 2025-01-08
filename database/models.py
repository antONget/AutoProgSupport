from sqlalchemy import String, Integer, DateTime, BigInteger, Boolean, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


engine = create_async_engine(url='sqlite+aiosqlite:///database/db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'Users'
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, default='user')


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
    photos_id: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    partner_list: Mapped[str] = mapped_column(String, default='')
    date_solution: Mapped[str] = mapped_column(String, default='')
    partner_solution: Mapped[int] = mapped_column(BigInteger, default=0)
    quality: Mapped[int] = mapped_column(BigInteger, default=-1)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


