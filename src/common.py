import datetime


def utc_tz(dt: datetime.datetime) -> datetime.datetime:
    return dt.replace(tzinfo=datetime.timezone.utc)


def no_tz(dt: datetime.datetime) -> datetime.datetime:
    return dt.replace(tzinfo=None)
