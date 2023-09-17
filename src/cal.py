import db
import pandas as pd
import datetime
import pytz
import pathlib

from icalendar import Calendar, Event

from typing import Any


def parse_rows(rows: list[db.TimerLogBase]) -> list[dict[str, Any]]:
    """
    Takes a list of db.TimerLogBase objects and returns a list of dicts
    which can then be used to create a dataframe
    """

    list_of_dicts = []

    for start, stop in zip(rows[::2], rows[1::2]):
        assert start.label == stop.label
        assert start.state == "start"
        assert stop.state == "stop"

        list_of_dicts.append(
            dict(
                label=start.label,
                start=start.ts,
                stop=stop.ts,
            )
        )

    return list_of_dicts


def create_cal_object(label: str, start: datetime.datetime, end: datetime.datetime, ts: datetime.datetime) -> Calendar():
    """
    Creates an icalendar.Calendar from label, start, end and ts datetime.datetime objects
    """

    assert isinstance(start, datetime.datetime)
    assert isinstance(end, datetime.datetime)
    assert isinstance(ts, datetime.datetime)

    # See: https://icalendar.readthedocs.io/en/latest/usage.html#example
    cal = Calendar()
    cal.add("prodid", "-//punch-card//github.com/algrt-hm/punch-card//")
    cal.add("version", "2.0")

    event = Event()
    event.add("summary", label)
    event.add("dtstart", start)
    event.add("dtend", end)
    event.add("dtstamp", ts)
    cal.add_component(event)

    return cal


def create_file_name(label: str, start: datetime.datetime, end: datetime.datetime, ts: datetime.datetime) -> str:
    """
    Returns filename string from label, start, end and ts datetime.datetime objects
    """

    assert isinstance(start, datetime.datetime)
    assert isinstance(end, datetime.datetime)
    assert isinstance(ts, datetime.datetime)

    def fmt(dt):
        return dt.strftime("%Y-%m-%d-%X").replace(":", "")

    extension = ".vcs"
    label = label.replace("-", "").replace(" ", "_").replace("/", "_")
    return "_".join([fmt(ts), label, fmt(start), fmt(end)]) + extension


def cal(date_of_interest: datetime.date) -> None:
    ts = datetime.datetime.now(tz=pytz.utc)
    df = pd.DataFrame(parse_rows(db.read_timer_log_date(date_of_interest)))

    if len(df) == 0:
        print(f"No records for {date_of_interest}")
        return
    else:
        print(df.to_markdown(index=False))

    for _, r in df.iterrows():
        params = dict(label=r.label, start=r.start, end=r.stop, ts=ts)
        cal = create_cal_object(**params)
        file_name = create_file_name(**params)
        pathlib.Path(file_name).write_bytes(cal.to_ical())
        print(f"{file_name} written")


if __name__ == "__main__":
    stop_date = datetime.date.today() - datetime.timedelta(days=7)

    while stop_date < datetime.date.today():
        cal(stop_date)
        stop_date += datetime.timedelta(days=1)
