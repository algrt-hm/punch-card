"""A simple app to track time, using textual"""

import argparse
import sys
import datetime
from app import runapp
from cal import cal
from sync import sync
from typing import Final


def main() -> int:
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        store_true: Final = "store_true"
        parser.add_argument("-a", "--app", help="Run the app!", action=store_true)
        parser.add_argument("-s", "--sync", help="Sync", action=store_true)
        # const actually means default and default means something else ...
        parser.add_argument("-c", "--calendar", help="Calendar times", type=str, const=str(datetime.date.today()), nargs="?")

    # Create the root argument parser and add global arguments
    parser = argparse.ArgumentParser(description="TODO")
    group = parser.add_mutually_exclusive_group()
    add_arguments(group)
    args: argparse.Namespace = parser.parse_args()

    # If run with no arguments mention -h
    if len(sys.argv) == 1:
        script_name = sys.argv[0]
        print(f"No flags provided, for usage please use:\n\tpython {script_name} -h")
        return 1

    if args.app:
        return runapp()

    if args.sync:
        sync()

    if args.calendar:
        date_ = datetime.date(*[int(x) for x in args.calendar.split("-")])
        cal(date_)

    return 0


if __name__ == "__main__":
    sys.exit(main())
