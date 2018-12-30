from argparse import ArgumentParser
import logging

from ucfai import groups_utils as grp_utils
from ucfai import ACCEPTED_GRP, ACCEPTED_OPS

# region ArgumentParser descriptions

# endregion


def main():
    logging.basicConfig()

    sem_meta = grp_utils.find_semester()

    parser = ArgumentParser(prog="ucfai")

    parser.add_argument("group", choices=ACCEPTED_GRP.keys())

    parser.add_argument("op", choices=ACCEPTED_OPS.keys())

    args = parser.parse_args()
    grp = ACCEPTED_GRP[args.group](sem_meta)
    ACCEPTED_OPS[args.op](grp)
