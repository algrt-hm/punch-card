from sync import *
from icecream import ic


def test_load_config():
    ret = load_config(file_name="test_creds.toml")
    expected = {"username": "testusername", "password": "testpassword", "host": "testhost", "database": "testdatabase"}
    assert ret == expected


def test_get_most_recent_state_timestamps():
    get_most_recent_state_timestamps(*get_local_remote_conn_str())
