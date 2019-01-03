import hashlib
import io
import os
import logging
from pathlib import Path
from typing import List, Dict

import imgkit
import requests
import yaml
from PIL import Image
from pandas import Timedelta, to_datetime, DataFrame, date_range, Series
from jinja2 import Template
import nbformat as nbf
import nbconvert as nbc

from ucfai.meta import MeetingMeta, meeting
from ucfai.meta.coordinator import Coordinator
from ucfai.meta.group import Group
from ucfai.meta.meeting import Meeting
from ucfai.tooling import OBS_HOLIDAY, UCF_CAL_URL
from ucfai.tooling.github_pages import SITE_CONTENT_DIR

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

res_dir = Path(__file__).parent


# region Public Methods ########################################################
# These should begin with a character.

def seed_semester(grp: Group) -> None:
    """Performs initial semester setup.
    1. Copies base YAML into `<grp>/<sem>/`
    2. Sets up the Website entries for the semester (doesn't make posts)
    3. Performs setup with Google Drive & Forms
    """
    __chk_root(grp)
    # Safety check.
    if grp.as_dir().exists():
        log.warning(f"I see that {grp.as_dir()} exists! Tread carefully.")
        raise ValueError(f"Found {grp.as_dir()}; exiting.")

    # region 1. Copy base YAML files {env, overhead, syllabus}.yml
    import shutil
    parent: Path = Path(__file__).parent
    # noinspection PyTypeChecker
    shutil.copytree(parent / "seed", grp.as_dir())

    # noinspection PyTypeChecker
    with open(grp.as_dir() / "env.yml", "r") as f:
        env = Template(f.read())

    # noinspection PyTypeChecker
    with open(grp.as_dir() / "env.yml", "w") as f:
        f.write(env.render(sem_meta=grp.sem))
    # endregion

    # region 2. Setup Website for this semester
    assert SITE_CONTENT_DIR.exists()
    (SITE_CONTENT_DIR / grp.as_dir()).mkdir()
    # endregion

    # region 3. Operate on Google Drive & Google Forms
    # TODO: make Google Drive folder for this semester

    # TODO: make "Sign Up" Google Form and Google Sheet

    # TODO: make "Sign Out" Google Form and Google Sheet
    # endregion


def prepare_ntbks(grp: Group) -> None:
    """Assumes a complete (or partially complete) Syllabus; this will only
    create new Syllabus entries and won't make other changes (to avoid
    irreversible deletions).
    """
    __chk_root(grp)

    # region Read `overhead.yml` and seed Coordinators
    # noinspection PyTypeChecker
    overhead = yaml.load(open(grp.as_dir() / "overhead.yml"))
    overhead_coordinators = overhead["coordinators"]
    setattr(grp, "coords", Coordinator.parse_yaml(overhead_coordinators))
    # endregion

    # region Read `syllabus.yml` and setup Notebooks
    # noinspection PyTypeChecker
    syllabus = yaml.load(open(grp.as_dir() / "syllabus.yml"))
    overhead_meetings = overhead["meetings"]

    def _parse_and_make_meetings(key: str) -> None:
        abbr = {"prim": "primary", "supp": "supplementary"}
        mtg_meta = __make_schedule(grp, overhead_meetings[abbr[key]])
        meetings = [Meeting(**Meeting.parse_yaml(mtg, grp.coords, meta))
                    for mtg, meta in zip(syllabus[abbr[key]], mtg_meta)]
        setattr(grp, f"{key}_sched", mtg_meta)

        for mtg in meetings:
            __make_notebook(grp, mtg)
            __prepares_post(grp, mtg)

    # region `Primary` meetings
    _parse_and_make_meetings("prim")
    # endregion
    # region `Supplementary` meetings
    if "supplementary" in syllabus.keys():
        _parse_and_make_meetings("supp")
    # endregion

    # endregion


def convert_ntbks(self) -> None:
    self.__chk_root()

    export = nbc.LatexExporter()
    export.template_path = res_dir / "templates" / "notebooks"
    export.template_file = "nb-as-post"

    # TODO: notebook conversion to Post w/ Front-Matter
# endregion


# region Accepted Operations
ACCEPTED_OPS = {
    "seed-semester": seed_semester,
    "prepare-ntbks": prepare_ntbks,
    "convert-ntbks": convert_ntbks,
}
# endregion


# region Private Methods #######################################################
# These should begin with "__"
def __day2idx(s: str) -> int:
    weekdays = "Mon Tue Wed Thu Fri".split()
    return weekdays.index(s)


def __chk_root(grp: Group) -> None:
    """Asserts that we're in the Jenkins root and not any subdirectories."""
    if "admin" in os.getcwd():
        os.chdir("..")  # shift up to parent directory if in `admin`
    assert repr(grp) not in os.getcwd(), \
        "Perform this operation from the Jenkins root, not the project root"


def __parse_ucf_cal(grp: Group) -> Series:
    holiday = OBS_HOLIDAY[grp.sem.name]
    cal_url = f"{UCF_CAL_URL}/json/{grp.meta.year}/{grp.meta.name}"

    ucf_parsed = requests.get(cal_url).json()["terms"][0]["events"]
    df_ucf_cal = DataFrame.from_dict(ucf_parsed)

    summary_mask = df_ucf_cal["summary"]
    beg = df_ucf_cal.loc[summary_mask.str.contains("Classes Begin")].iloc[0]
    end = df_ucf_cal.loc[summary_mask.str.contains("Classes End")].iloc[0]

    # generate a DataFrame with all possible dates (to act like a calendar)
    #   there's also the [7:] slicer b/c we can't meet in the first week of
    #   the semester, according to UCF
    dt_range = Series(date_range(beg["dtstart"][:-1],
                                 end["dtstart"][:-1]))[7:]

    dt_holidays = None  # TODO: figure generalized removal, later

    return dt_range


def __make_schedule(grp: Group, sched: Dict) -> List[MeetingMeta]:
    dt_range = __parse_ucf_cal(grp)
    assert all([v for v in sched.values()])

    wday, room = sched["wday"], sched["room"]

    time_s, time_e = sched["time"].split("-")
    mtg_time = Timedelta(hours=int(time_s[:2]), minutes=int(time_s[3:]))
    dt_range += mtg_time

    mtg_dts = dt_range.iloc[__day2idx(wday)::7].values
    log.info("Meeting dates:\n%s", mtg_dts)

    sched = [MeetingMeta(to_datetime(mtg), room) for mtg in mtg_dts]
    log.debug(sched)

    return sched


def __make_notebook(grp: Group, mtg: Meeting) -> None:
    path = grp.as_dir() / mtg.as_nb()
    if path.exists():
        raise FileExistsError("I won't overwrite this file. :/")

    Path(path.parent).mkdir()

    nb = nbf.v4.new_notebook()
    nb["metadata"] = meeting.metadata(mtg)
    nb["cells"].append(meeting.heading(mtg, repr(grp)))

    with open(path, "w") as f_nb:
        nbf.write(nb, f_nb)


def __prepares_post(grp: Group, mtg: Meeting) -> None:
    path = SITE_CONTENT_DIR / grp.as_dir() / str(mtg)
    if path.exists():
        raise FileExistsError("Erm... the entry for the site exists. :/")

    path.mkdir()


def __make_banner(mtg: Meeting) -> None:
    """Generates the banner for each meeting."""

    # region meta, needed to generate the banner and restrict images
    tpl_banner = Template(
        open(res_dir / "templates" / "event-banner.html").read())

    accepted_content_types = list(map(
        lambda x: f"image/{x}", ["jpeg", "png", "gif", "tiff"]
    ))
    # endregion

    # region snag banner image from url
    ext = mtg.covr.split(".")[-1]
    cvr = requests.get(mtg.covr, headers={"user-agent": "Mozilla/5.0"})
    cvr_pth = Group.workdir(str(mtg), "cover." + ext)
    if cvr.headers["Content-Type"] in accepted_content_types:
        img_bytes = io.BytesIO(cvr.content)
        try:
            # noinspection PyTypeChecker
            cvr_bytes = io.BytesIO(open(cvr_pth, "rb").read())

            # get hashes to check for diff
            cvr_hash = hashlib.sha256(cvr_bytes).hexdigest()
            img_hash = hashlib.sha256(img_bytes).hexdigest()

            if cvr_hash != img_hash:
                img = Image.open(img_bytes)
                img.save(cvr_pth)
        except FileNotFoundError:
            pass
    # endregion

    # region render the banner and save
    out = Group.workdir(str(mtg), "banner.jpg")

    banner = tpl_banner.render(
        date=mtg.meta.date,
        room=mtg.meta.room,
        name=mtg.name.encode("ascii", "xmlcharrefreplace").decode("utf-8"),
        cover=cvr_pth
    )
    imgkit.from_string(banner, out, options={"quiet": ""})
    # endregion

# endregion
