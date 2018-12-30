from datetime import (
    datetime as dt
)
from pathlib import Path
from typing import List, Dict
import logging

import requests
import pandas as pd
from jinja2 import Template

from ucfai import MeetingMeta, SemesterMeta
from .groups import Group

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

ucf_cal_url = "https://calendar.ucf.edu"
obs_holiday = {
    "spring": ["Spring Break", "Martin Luther King Jr. Day", ],
    "fall": ["Veterans Day", "Labor Day", "Thanksgiving", ],
}


def day2idx(s: str) -> int:
    weekdays = "Mon Tue Wed Thu Fri".split()
    return weekdays.index(s)


def find_semester() -> SemesterMeta:
    cal_url = requests.get(ucf_cal_url).url
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

    year, name = cal_url.replace(f"{ucf_cal_url}/", "").split("/")
    short = name[:2] + year[2:]

    return SemesterMeta(name, year, short)


def parse_ucf_cal(sem_meta: SemesterMeta) -> pd.Series:
    from pandas import date_range, Series, DataFrame
    holiday = obs_holiday[sem_meta.name]
    cal_url = f"{ucf_cal_url}/json/{sem_meta.year}/{sem_meta.name}"

    ucf_parsed = requests.get(cal_url).json()["terms"][0]["events"]
    df_ucf_cal = DataFrame.from_dict(ucf_parsed)

    summary_mask = df_ucf_cal["summary"]
    beg = df_ucf_cal.loc[summary_mask.str.contains("Classes Begin")].iloc[0]
    end = df_ucf_cal.loc[summary_mask.str.contains("Classes End")].iloc[0]

    # generate a DataFrame with all possible dates (to act like a calendar)
    #   there's also the [7:] slicer b/c we can't meet in the first week of
    #   the semester, according to UCF
    dt_range = Series(date_range(beg["dtstart"][:-1], end["dtstart"][:-1]))[7:]

    dt_holidays = None  # TODO: figure generalized removal, later

    return dt_range


def make_schedule(sched_yaml: Dict) -> List[MeetingMeta]:
    semester = find_semester()
    dt_range = parse_ucf_cal(semester)

    from pandas import Timedelta, to_datetime
    assert all([v for v in sched_yaml.values()])

    wday, room = sched_yaml["wday"], sched_yaml["room"]

    time_s, time_e = sched_yaml["time"].split("-")
    mtg_time = Timedelta(hours=int(time_s[:2]), minutes=int(time_s[3:]))
    dt_range += mtg_time

    mtg_dts = dt_range.iloc[day2idx(wday)::7].values
    log.info("Meeting dates:\n%s", mtg_dts)

    sched = [MeetingMeta(to_datetime(mtg), room) for mtg in mtg_dts]
    log.debug(sched)

    return sched


def __check_root(group: Group) -> None:
    import os
    if "admin" in os.getcwd():
        os.chdir("..")  # shift up to the parent directory if in "admin"
    assert repr(group) not in os.getcwd()


def seed_semester(group: Group) -> None:
    __check_root(group)
    desired = group._to_dir()

    if desired.exists():
        log.warning(f"I see that {str(desired)} exists! Tread carefully.")
        raise ValueError(f"Found {str(desired)}; no fail-safe exists; exiting.")

    import shutil
    module_parent = Path(__file__).parent
    shutil.copytree(module_parent / "yaml_tpl", desired)

    with open(desired / "env.yml", "r") as f:
        env = Template(f.read())

    with open(desired / "env.yml", "w") as f:
        env = env.render(sem_meta=group.sem)
        f.write(env)

    from .website import site_content_dir
    assert site_content_dir.exists()
    (site_content_dir / group._to_dir()).mkdir()


def prepare_ntbks(group: Group) -> None:
    __check_root(group)
    overhead = group._to_dir() / "overhead.yml"
    syllabus = group._to_dir() / "syllabus.yml"

    import yaml
    # region overhead
    overhead = yaml.load(open(overhead))
    from .coordinator import Coordinator

    def _parse_coordinators(coordinators: List) -> Dict:
        return {c["github"]: Coordinator(**c) for c in coordinators}

    coords = _parse_coordinators(overhead["coordinators"])
    setattr(group, "coords", coords)
    # endregion

    # region syllabus
    syllabus = yaml.load(open(syllabus))
    from .meeting import Meeting
    overhead_meetings = overhead["meetings"]

    def _parse_and_make_mtgs(key: str) -> None:
        abbr = {"prim": "primary", "supp": "supplementary"}
        mtg_meta = make_schedule(overhead_meetings[abbr[key]])
        meetings = [Meeting(**Meeting.parse_yaml(mtg, group.coords, meta))
                    for mtg, meta in zip(syllabus[abbr[key]], mtg_meta)]
        setattr(group, f"{key}_mtgs", meetings)

        for mtg in meetings:
            mtg.make_ntbk(group)
            mtg.prep_post(group)

    # region primary meetings
    _parse_and_make_mtgs("prim")
    # endregion

    # region secondary meetings, if defined
    if "supplementary" in syllabus.keys():
        _parse_and_make_mtgs("supp")
    # endregion

    # endregion


def convert_ntbks(group: Group):
    __check_root(group)

    from nbconvert import LatexExporter
    export = LatexExporter()
    export.template_path = Path(__file__).parent / "html_tpl"
    export.template_file = "nb-as-post"

    # TODO: redo notebook conversions
