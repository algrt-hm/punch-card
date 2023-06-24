from src.db import *
from typing import Any
from rich import print as pprint

# Unused
def mock_internal_log() -> list[list[dict[str, Any]]]:
    return [
        [
            {
                "label": "Job/interview prep",
                "state": "start",
                "ts": datetime.datetime(2023, 6, 24, 10, 22, 40, 201346, tzinfo=datetime.timezone.utc),
                "date": datetime.date(2023, 6, 24),
            },
            {
                "label": "Job/interview prep",
                "state": "stop",
                "ts": datetime.datetime(2023, 6, 24, 10, 22, 40, 621774, tzinfo=datetime.timezone.utc),
                "date": datetime.date(2023, 6, 24),
            },
        ],
        [
            {
                "label": "Personal finance",
                "state": "start",
                "ts": datetime.datetime(2023, 6, 24, 10, 22, 38, 4337, tzinfo=datetime.timezone.utc),
                "date": datetime.date(2023, 6, 24),
            },
            {
                "label": "Personal finance",
                "state": "stop",
                "ts": datetime.datetime(2023, 6, 24, 10, 22, 38, 376248, tzinfo=datetime.timezone.utc),
                "date": datetime.date(2023, 6, 24),
            },
        ],
    ]

# Unused
def mock_internal_log() -> list[list[dict[str, Any]]]:
    return [
        [
            {
                "label": "Job/interview prep",
                "state": "start",
                "ts": datetime.datetime(2023, 6, 24, 10, 22, 40, 201346, tzinfo=datetime.timezone.utc),
                "date": datetime.date(2023, 6, 24),
            },
            {
                "label": "Job/interview prep",
                "state": "stop",
                "ts": datetime.datetime(2023, 6, 24, 10, 22, 40, 621774, tzinfo=datetime.timezone.utc),
                "date": datetime.date(2023, 6, 24),
            },
        ],
        [
            {
                "label": "Personal finance",
                "state": "start",
                "ts": datetime.datetime(2023, 6, 24, 10, 22, 38, 4337, tzinfo=datetime.timezone.utc),
                "date": datetime.date(2023, 6, 24),
            },
            {
                "label": "Personal finance",
                "state": "stop",
                "ts": datetime.datetime(2023, 6, 24, 10, 22, 38, 376248, tzinfo=datetime.timezone.utc),
                "date": datetime.date(2023, 6, 24),
            },
        ],
    ]

# Unused
def totals_from_internal_log(l_of_l_of_d=mock_internal_log()) -> dict[str, float]:
    totals = dict()

    for list in l_of_l_of_d:
        label = list[0]["label"]
        starts = []
        stops = []
        for row in list:
            assert row["label"] == label
            if row["state"] == "start":
                starts.append(row)
            elif row["state"] == "stop":
                stops.append(row)
            else:
                raise Exception("Unknown state")

        totals[label] = sum([datetime.datetime.timestamp(row["ts"]) for row in stops]) - sum([datetime.datetime.timestamp(row["ts"]) for row in starts])

    return totals


def totals_from_db_log(log) -> dict[str, float]:
    # First get the set of labels
    labels = set()

    for row in log:
        if row.label not in labels:
            labels.add(row.label)

    # For each label, get the last state
    totals = dict()
    for label in labels:
        starts = []
        stops = []
        for row in [row for row in log if row.label == label]:
            if row.state == "start":
                starts.append(row)
            elif row.state == "stop":
                stops.append(row)
            else:
                raise Exception("Unknown state")
            # Start and stop must be the same number of occurrences
        assert len(starts) == len(stops)

        # Sum stops, subtract starts
        totals[label] = sum([datetime.datetime.timestamp(row.ts) for row in stops]) - sum([datetime.datetime.timestamp(row.ts) for row in starts])

    return totals


def test_db_reconcile():
    conn_str = default_db_url

    state = read_state(conn_str=conn_str)
    log = read_timer_log(conn_str=conn_str)

    pprint(totals_from_db_log(log))
    pprint(totals_from_internal_log())
