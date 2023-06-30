import sqlalchemy
import datetime
import pydantic
import sqlalchemy.orm
import functools
from typing import Any, Final

default_db_name: Final[str] = "punch-card"
default_db_url: Final[str] = f"sqlite:///{default_db_name}.sqlite3"

# metadata for sqlalchemy tables
metadata = sqlalchemy.MetaData()

# delcarative base class for sqlalchmey
Base = sqlalchemy.orm.declarative_base()

###
# database setup for log
###


# pydantic class
class TimerLogPydantic(pydantic.BaseModel):
    label: str
    state: str
    date: datetime.date
    ts: datetime.datetime


# table info for DDL creation etc
timer_log_table = sqlalchemy.Table(
    "timer_log",
    metadata,
    sqlalchemy.Column("label", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("state", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("date", sqlalchemy.Date, nullable=False),
    sqlalchemy.Column("ts", sqlalchemy.DateTime(timezone=True), primary_key=True),
)


# class to take in pydantic class
class TimerLogBase(Base):
    __tablename__ = "timer_log"

    label = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    state = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    ts = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True), primary_key=True)

    def __repr__(self) -> str:
        return f"TimerLogDB(label={self.label!r}, state={self.state!r}), date={self.date!r}), ts={self.ts!r})"


###
# database setup for state
###


# pydantic class
class TimerStatePydantic(pydantic.BaseModel):
    label: str
    elapsed: float
    ts: datetime.datetime


# table info for DDL creation etc
timer_state_table = sqlalchemy.Table(
    "timer_state",
    metadata,
    sqlalchemy.Column("label", sqlalchemy.Text, primary_key=True),
    sqlalchemy.Column("elapsed", sqlalchemy.Float, nullable=False),
    sqlalchemy.Column("ts", sqlalchemy.DateTime(timezone=True)),
)


# class to take in pydantic class
class TimerStateBase(Base):
    __tablename__ = "timer_state"

    label = sqlalchemy.Column(sqlalchemy.Text, primary_key=True)
    elapsed = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    ts = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"TimerStateDB(label={self.label!r}, elapsed={self.elapsed!r}, ts={self.ts!r})"


###
# Some helper functions to abstract away inserts etc
###


@functools.cache
def get_engine_and_ddl(conn_str: str) -> sqlalchemy.engine.base.Engine:
    engine = sqlalchemy.create_engine(conn_str)

    # check we have what we expect from the matadata, otherwise
    # get the DLL done
    expected_tables = metadata.tables.keys()
    inspector = sqlalchemy.inspect(engine)
    have_tables = inspector.get_table_names()

    if set(have_tables) == set(expected_tables):
        # Expected tables are the same as existing tables"
        pass
    else:
        # Have {have_tables} tables, expect {expected_tables} tables, will create
        metadata.create_all(engine)

    return engine


@functools.cache
def get_test_engine() -> sqlalchemy.engine.base.Engine:
    return sqlalchemy.create_engine("sqlite:///", echo=True)


@functools.cache
def get_test_engine_and_session() -> tuple[sqlalchemy.engine.base.Engine, sqlalchemy.orm.session.sessionmaker]:
    # in-memory sqlite
    engine = get_test_engine()
    # a sessionmaker(), also in the same scope as the engine
    Session = sqlalchemy.orm.sessionmaker(engine)
    return engine, Session


@functools.cache
def get_session(conn_str: str) -> sqlalchemy.orm.session.Session:
    # This seems a bit convoluted but it doesn't feel tidy to for Session() to be global
    # this will be whatever store
    engine = get_engine_and_ddl(conn_str=conn_str)
    # a sessionmaker(), also in the same scope as the engine
    Session = sqlalchemy.orm.sessionmaker(engine)
    return Session()


def write_timer_log(row: dict[Any], conn_str: str = default_db_url) -> None:
    # Put into pydantic class first so we catch any issues
    stg = TimerLogPydantic(**row)
    insert_data = TimerLogBase(label=stg.label, state=stg.state, date=stg.date, ts=stg.ts)
    with get_session(conn_str=conn_str) as session:
        session.add(insert_data)
        session.commit()


def read_timer_log(conn_str: str = default_db_url) -> list[TimerLogBase]:
    with get_session(conn_str=conn_str) as session:
        statement = sqlalchemy.select(TimerLogBase).order_by(TimerLogBase.ts)
        ret = session.scalars(statement).all()
    return ret


def read_timer_log_date(date: datetime.date, conn_str: str = default_db_url) -> list[TimerLogBase]:
    with get_session(conn_str=conn_str) as session:
        statement = sqlalchemy.select(TimerLogBase).where(TimerLogBase.date == date).order_by(TimerLogBase.ts)
        ret = session.scalars(statement).all()
    return ret


def clear_state(conn_str: str = default_db_url) -> None:
    stmt = sqlalchemy.delete(TimerStateBase)
    with get_session(conn_str=conn_str) as session:
        session.execute(stmt)
        session.commit()


def write_state(row: dict[Any], conn_str: str = default_db_url) -> None:
    # Put into pydantic class first so we catch any issues
    stg = TimerStatePydantic(**row)
    insert_data = TimerStateBase(label=stg.label, elapsed=stg.elapsed, ts=stg.ts)

    with get_session(conn_str=conn_str) as session:
        session.add(insert_data)
        session.commit()


def read_state(conn_str: str = default_db_url) -> list[TimerStateBase]:
    with get_session(conn_str=conn_str) as session:
        statement = sqlalchemy.select(TimerStateBase)
        ret = session.scalars(statement).all()
    return ret
