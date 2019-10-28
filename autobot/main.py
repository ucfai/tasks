from argparse import ArgumentParser
import logging
from datetime import datetime as dt

import requests
import argcomplete

from autobot.meta import groups
from autobot.lib import ops
from autobot.lib.apis import ucf
from autobot.lib import safety


def main():
    logging.basicConfig()

    semester = ucf.determine_semester().short

    parser = ArgumentParser(prog="autobot")

    parser.add_argument("group", choices=groups.ACCEPTED.keys())
    parser.add_argument("op", choices=ops.ACCEPTED.keys())
    parser.add_argument("semester", nargs="?", default=semester)
    parser.add_argument("--overwrite", action="store_true")

    argcomplete.autocomplete(parser)

    args = parser.parse_args()
    args.semester = ucf.semester_converter(short=semester)

    # `groups.ACCEPTED` makes use of Python's dict-based execution to allow for
    #   restriction to one of the Groups listed in `meta/groups.py`
    group = groups.ACCEPTED[args.group](args.semester)

    safety.force_root()

    # `ops.ACCEPTED` does similarly, restricting execution to the opterations
    #   lists in `lib/ops.py`
    ops.ACCEPTED[args.op](group, args.overwrite)
