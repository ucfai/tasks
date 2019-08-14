from argparse import ArgumentParser
import logging
from datetime import datetime as dt

import requests

from autobot.meta import groups
from autobot.lib import ops
from autobot.lib.apis.ucf import determine_semester


def main():
    logging.basicConfig()

    sem_meta = determine_semester()

    parser = ArgumentParser(prog="autobot")

    parser.add_argument("group", choices=groups.ACCEPTED.keys())
    parser.add_argument("op", choices=ops.ACCEPTED.keys())
    parser.add_argument("--full-overwrite", action="store_true", dest="overwrite")

    args = parser.parse_args()

    # `groups.ACCEPTED` makes use of Python's dict-based execution to allow for
    #   restriction to one of the Groups listed in `meta/groups.py`
    group = groups.ACCEPTED[args.group](sem_meta)

    # `ops.ACCEPTED` does similarly, restricting execution to the opterations
    #   lists in `lib/ops.py`
    ops.ACCEPTED[args.op](group, args.overwrite)
