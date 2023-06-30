import tomllib
import pathlib
import datetime

import db
import sqlalchemy
from rich import print as pprint

from common import utc_tz

from typing import Final, Any

default_file_name: Final[str] = "creds.toml"
username: Final[str] = "username"
password: Final[str] = "password"
host: Final[str] = "host"
database: Final[str] = "database"


# Load the configuration file
def load_config(file_name: str = default_file_name) -> dict[str, Any]:
    """
    Reads config.  Anticipates the config file to be in TOML format like this:

    [database]
    username = "postgres"
    password = ""
    host = "hansolo"
    database = "punch_card"
    """

    expected_keys = [username, password, host, database]
    path = (pathlib.Path(__file__) / ".." / ".." / file_name).resolve()

    if not path.exists():
        raise Exception(f"{path} does not seem to exist")

    config = tomllib.loads(path.read_text())

    if database not in config:
        raise Exception(f"{database} not found in {path}")

    config = config[database]

    if set(expected_keys) != set(config.keys()):
        raise Exception(f"Config in {path} must contain {expected_keys}")

    return config


def config_to_conn_str(config: dict[str, Any]) -> sqlalchemy.engine.URL:
    return sqlalchemy.engine.URL.create(
        drivername="postgresql",
        username=config[username],
        password=config[password],
        host=config[host],
        database=config[database],
    )


def row_to_dict(row: db.TimerLogBase) -> dict[str, Any]:
    return dict(label=row.label, state=row.state, date=row.date, ts=row.ts)


def get_local_remote_conn_str() -> tuple[str, str]:
    local_conn_str = db.default_db_url
    remote_conn_str = config_to_conn_str(config=load_config())

    return local_conn_str, remote_conn_str


def get_most_recent_state_timestamps(local_conn_str: str, remote_conn_str: str) -> tuple[datetime.datetime, datetime.datetime]:
    local_conn_str, remote_conn_str = get_local_remote_conn_str()
    old = utc_tz(datetime.datetime(1900, 1, 1))
    max_local, max_remote = old, old

    local_states = db.read_state(conn_str=local_conn_str)
    remote_states = db.read_state(conn_str=remote_conn_str)

    # Loop through to get the latest
    for state in local_states:
        ts = utc_tz(state.ts)
        if ts > max_local:
            max_local = ts

    for state in remote_states:
        ts = utc_tz(state.ts)
        if ts > max_remote:
            max_remote = ts

    return max_local, max_remote


def sync() -> None:
    local_symbol: Final[str] = "<"
    remote_symbol: Final[str] = ">"

    local_conn_str, remote_conn_str = get_local_remote_conn_str()
    remote_engine = db.get_engine_and_ddl(conn_str=remote_conn_str)
    local_engine = db.get_engine_and_ddl(conn_str=local_conn_str)

    print(f"Local: {local_engine}")
    print(f"Remote: {remote_engine}")

    # State
    # Compare timestamps to see which is more recent
    local_ts, remote_ts = get_most_recent_state_timestamps(local_conn_str, remote_conn_str)

    if remote_ts > local_ts:
        # Get state from remote to local (local is overwritten)
        list_of_state = db.read_state(conn_str=remote_conn_str)
        db.clear_state(conn_str=local_conn_str)
        print(f"state table cleared (locally)")
        for row in list_of_state:
            db.write_state(dict(label=row.label, elapsed=row.elapsed, ts=row.ts), conn_str=local_conn_str)
            print(f"{local_symbol} {row} written (locally)")
    elif local_ts > remote_ts:
        # Send state from local to remote (remote is overwritten)
        list_of_state = db.read_state(conn_str=local_conn_str)
        db.clear_state(conn_str=remote_conn_str)
        print(f"state table cleared (remotely)")
        for row in list_of_state:
            db.write_state(dict(label=row.label, elapsed=row.elapsed, ts=row.ts), conn_str=remote_conn_str)
            print(f"{remote_symbol} {row} written (remotely)")
    else:
        pprint("Looks like state already synced, not doing anything :grinning_face:")

    # Log
    local_dict = {utc_tz(row.ts): row_to_dict(row) for row in db.read_timer_log(conn_str=local_conn_str)}
    remote_dict = {utc_tz(row.ts): row_to_dict(row) for row in db.read_timer_log(conn_str=remote_conn_str)}

    # Anything in local not in remote gets written to remote
    for ts in local_dict.keys():
        if ts not in remote_dict.keys():
            row_dict = local_dict[ts]
            db.write_timer_log(row_dict, conn_str=remote_conn_str)
            print(f"{remote_symbol} {row_dict} written")

    # Anything in remote not in local gets written to local
    for ts in remote_dict.keys():
        if ts not in local_dict.keys():
            row_dict = remote_dict[ts]
            db.write_timer_log(row_dict, conn_str=local_conn_str)
            print(f"{local_symbol} {row_dict} written")


if __name__ == "__main__":
    sync()
