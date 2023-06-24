import pandas as pd

import db
import datetime
from common import no_tz

from typing import Any


rows = db.read_timer_log()


def parse_rows() -> list[dict[str, Any]]:
    l = []

    for start, stop in zip(rows[::2], rows[1::2]):
        assert start.label == stop.label
        assert start.state == "start"
        assert stop.state == "stop"

        l.append(
            dict(
                label=start.label,
                start=start.ts,
                stop=stop.ts,
            )
        )

    return l


# Step 2: write a calendar file for each
df = pd.DataFrame(parse_rows())
df["elapsed"] = (df.stop - df.start).dt.total_seconds()
df_gb = df[["label", "elapsed"]].groupby("label").sum().reset_index()
print(df_gb)

now = no_tz(datetime.datetime.now(tz=datetime.timezone.utc))

delete_ = "delete from timer_state;"
s = "\n".join([f"""insert into timer_state (label, elapsed, ts) values ('{r.label}', {r.elapsed}, '{now}');""" for _, r in df_gb.iterrows()])
print(delete_, s, sep="\n")
