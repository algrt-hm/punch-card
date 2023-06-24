import sqlalchemy
import datetime

from src.db import (
    get_test_engine_and_session,
    metadata,
    TimerLogPydantic,
    TimerStatePydantic,
    TimerLogBase,
    TimerStateBase,
)

# get test engine and session
engine, Session = get_test_engine_and_session()
# create table(s)
metadata.create_all(engine)
# a timestamp to use in tests
raw_ts = datetime.datetime.utcnow()
ts = raw_ts.replace(tzinfo=datetime.timezone.utc)


def timer_log_mock():
    external_data = {"label": "label", "state": "state", "date": ts.date(), "ts": ts}
    return TimerLogPydantic(**external_data)


def state_mock():
    external_data = {"label": "label", "state": "state", "elapsed": 1.1, "ts": ts}
    return TimerStatePydantic(**external_data)


def write_to_log_db():
    d = timer_log_mock()
    insert_data = TimerLogBase(label=d.label, state=d.state, date=d.date, ts=d.ts)
    with Session() as session:
        session.add(insert_data)
        session.commit()


def read_from_log_db():
    with Session() as session:
        statement = sqlalchemy.select(TimerLogBase)
        ret = session.scalars(statement).all()
    return ret


def write_to_state_db():
    d = state_mock()
    insert_data = TimerStateBase(label=d.label, elapsed=d.elapsed, ts=d.ts)
    with Session() as session:
        session.add(insert_data)
        session.commit()


def read_from_state_db():
    with Session() as session:
        statement = sqlalchemy.select(TimerStateBase)
        ret = session.scalars(statement).all()
    return ret


def test_write_to_db():
    write_to_log_db()
    write_to_state_db()


def test_read_from_db():
    for row in read_from_log_db():
        print(row)

    # sqlite will lose the tz-info, postgres will keep
    # so we're happy to have either
    with_tz = str(row) == str(TimerLogBase(label="label", state="state", date=ts.date(), ts=ts))
    without_tz = str(row) == str(TimerLogBase(label="label", state="state", date=ts.date(), ts=raw_ts))
    assert with_tz or without_tz

    for row in read_from_state_db():
        print(row)

    with_tz = str(row) == str(TimerStateBase(label="label", elapsed=1.1, ts=ts))
    without_tz = str(row) == str(TimerStateBase(label="label", elapsed=1.1, ts=raw_ts))
    assert with_tz or without_tz
