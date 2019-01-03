from argparse import ArgumentParser
import logging
from datetime import datetime as dt

import requests

from ucfai.meta import SemesterMeta, ACCEPTED_GRP
from ucfai.tooling import UCF_CAL_URL, ACCEPTED_OPS


# region ArgumentParser descriptions

# endregion


def which_semester() -> SemesterMeta:
    """A static method which determines the current semester based on the
    present date and uses the UCF calendar redirect to inform its decision.

    :return: SemesterMeta
    """
    cal_url = requests.get(UCF_CAL_URL).url
    curr_dt = dt.now()

    may, aug, dec = [5, 8, 12]  # May, Aug, Dec (1-based)

    if curr_dt.month in [may, aug, dec]:
        if cal_url.endswith("fall") and curr_dt.month == dec:
            cal_url = cal_url.replace("fall", "spring").replace(
                f"{curr_dt.year}", f"{curr_dt.year + 1}"
            )
        elif cal_url.endswith("summer") and curr_dt.month == aug:
            cal_url = cal_url.replace("summer", "fall")
        elif cal_url.endswith("spring") and curr_dt.month == may:
            cal_url = cal_url.replace("spring", "summer")

    year, name = cal_url.replace(f"{UCF_CAL_URL}/", "").split("/")
    short = name[:2] + year[2:]

    return SemesterMeta(name, year, short)


def main():
    logging.basicConfig()

    sem_meta = which_semester()

    parser = ArgumentParser(prog="ucfai")

    parser.add_argument("group", choices=ACCEPTED_GRP.keys())

    parser.add_argument("op", choices=ACCEPTED_OPS.keys())

    args = parser.parse_args()
    grp = ACCEPTED_GRP[args.group](sem_meta)
    ACCEPTED_OPS[args.op](grp)
