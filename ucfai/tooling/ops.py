import io
import os
import logging
import datetime
from pathlib import Path
from typing import List, Dict

import imgkit
import requests
import yaml
from PIL import Image
from pandas import Timedelta, to_datetime, DataFrame, date_range, Series, concat
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

res_dir = Path(__file__).parent.parent

today = to_datetime(datetime.date.today())

# region Public Methods ########################################################
# These should begin with a character.

def seed_semester(grp: Group, auto_overwrite: bool = False) -> None:
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
    # noinspection PyTypeChecker
    shutil.copytree(res_dir / "templates/seed", grp.as_dir())

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


def prepare_ntbks(grp: Group, auto_overwrite: bool = False) -> None:
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
    _mtg_offset = overhead_meetings["start_offset"]
    
    def _can_overwrite():
        s = "It seems that you're attempting to overwrite a passed meeting. " \
            "Shall I continue? [y/N] "
        return input(s).lower() == "y"

    def _parse_and_make_meetings(key: str) -> None:
        abbr = {"prim": "primary", "supp": "supplementary"}
        mtg_meta = __make_schedule(grp, overhead_meetings[abbr[key]],
                                   offset=_mtg_offset)
        meetings = [Meeting(**Meeting.parse_yaml(mtg, grp.coords, meta))
                    for mtg, meta in zip(syllabus[abbr[key]], mtg_meta)]
        setattr(grp, f"{key}_sched", mtg_meta)

        for mtg in meetings:
            manual_overwrite = False
            if mtg.meta.date < today:
                manual_overwrite = _can_overwrite()
            if manual_overwrite or (auto_overwrite and mtg.meta.date > today):
                __make_notebook(grp, mtg, auto_overwrite)
                __prepares_post(grp, mtg, auto_overwrite)

    # region `Primary` meetings
    _parse_and_make_meetings("prim")
    # endregion
    # region `Supplementary` meetings
    if "supplementary" in syllabus.keys():
        _mtg_offset += 1
        _parse_and_make_meetings("supp")
    # endregion

    # endregion
    

def update_ntbks(grp: Group, auto_overwrite: bool = False) -> None:
    """Assumes the existence of the Syllabus; this will attempt to update
    notebooks and produce banners for the semester."""
    __chk_root(grp)
    
    # region Read `overhead.yml` and update Coordinators
    # noinspection PyTypeChecker
    overhead = yaml.load(open(grp.as_dir() / "overhead.yml"))
    overhead_coordinators = overhead["coordinators"]
    setattr(grp, "coords", Coordinator.parse_yaml(overhead_coordinators))
    # endregion
    
    # region Read `syllabus.yml`; update Notebooks; make banners
    syllabus = yaml.load(open(grp.as_dir() / "syllabus.yml"))
    overhead_meetings = overhead["meetings"]
    _mtg_offset = overhead_meetings["start_offset"]
    
    def _can_overwrite():
        s = "It appears that you might be overwriting a passed meeting " \
            "banner. Shall I continue? [y/N] "
        return input(s) == "y"
    
    def _parse_and_make_meetings(key: str) -> None:
        abbr = {"prim": "primary", "supp": "supplementary"}
        mtg_meta = __make_schedule(grp, overhead_meetings[abbr[key]],
                                   offset=_mtg_offset)
        meetings = [Meeting(**Meeting.parse_yaml(mtg, grp.coords, meta))
                    for mtg, meta in zip(syllabus[abbr[key]], mtg_meta)]
        setattr(grp, f"{key}_sched", mtg_meta)

        for mtg in meetings:
            manual_overwrite = False
            if mtg.meta.date < today:
                manual_overwrite = _can_overwrite()
            if manual_overwrite or (auto_overwrite and mtg.meta.date > today):
                __make_banner(grp, mtg)

    # region `Primary` meetings
    _parse_and_make_meetings("prim")
    # endregion
    
    # region `Supplementary` meetings
    if "supplementary" in syllabus.keys():
        _mtg_offset += 1
        _parse_and_make_meetings("supp")
    # endregion
    
    # endregion


def convert_ntbks(grp: Group) -> None:
    __chk_root(grp)

    # TODO: notebook conversion to Post w/ Front-Matter
    # region Read `overhead.yml` and update Coordinators
    # noinspection PyTypeChecker
    overhead = yaml.load(open(grp.as_dir() / "overhead.yml"))
    overhead_coordinators = overhead["coordinators"]
    setattr(grp, "coords", Coordinator.parse_yaml(overhead_coordinators))
    # endregion

    # region Read `syllabus.yml`; update Notebooks; make banners
    syllabus = yaml.load(open(grp.as_dir() / "syllabus.yml"))
    overhead_meetings = overhead["meetings"]
    _mtg_offset = overhead_meetings["start_offset"]

    def _parse_and_make_meetings(key: str) -> None:
        abbr = {"prim": "primary", "supp": "supplementary"}
        mtg_meta = __make_schedule(grp, overhead_meetings[abbr[key]],
                                   offset=_mtg_offset)
        meetings = [Meeting(**Meeting.parse_yaml(mtg, grp.coords, meta))
                    for mtg, meta in zip(syllabus[abbr[key]], mtg_meta)]
        setattr(grp, f"{key}_sched", mtg_meta)
    
        for mtg in meetings:
            __make_posts(grp, mtg)

    # region `Primary` meetings
    _parse_and_make_meetings("prim")
    # endregion

    # region `Supplementary` meetings
    if "supplementary" in syllabus.keys():
        _mtg_offset += 1
        _parse_and_make_meetings("supp")
    # endregion
# endregion


# region Accepted Operations
ACCEPTED_OPS = {
    "seed-semester": seed_semester,
    "prepare-ntbks": prepare_ntbks,
    "update-ntbks" : update_ntbks,
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
    cal_url = f"{UCF_CAL_URL}/json/{grp.sem.year}/{grp.sem.name}"

    ucf_parsed = requests.get(cal_url).json()["terms"][0]["events"]
    df_ucf_cal = DataFrame.from_dict(ucf_parsed)

    summary_mask = df_ucf_cal["summary"]
    beg = df_ucf_cal.loc[summary_mask.str.contains("Classes Begin")].iloc[0]
    end = df_ucf_cal.loc[summary_mask.str.contains("Classes End")].iloc[0]

    # generate a DataFrame with all possible dates (to act like a calendar)
    #   there's also the [7:] slicer b/c we can't meet in the first week of
    #   the semester, according to UCF
    dt_range = Series(date_range(start=beg["dtstart"][:-1],
                                 end=end["dtstart"][:-1]))[7:]

    dt_holis = []
    for h in holiday:
        day2rm = df_ucf_cal.loc[summary_mask.str.contains(h)].iloc[0]
        beg = day2rm["dtstart"][:-1]
        end = day2rm["dtend"][:-1] if day2rm["dtend"] else beg
        dt_holis.append(Series(date_range(start=beg, end=end)))
    
    dt_holis = concat(dt_holis)

    return dt_range, dt_holis


def __make_schedule(grp: Group, sched: Dict, offset: int = 3) -> List[MeetingMeta]:
    dt_range, dt_holis = __parse_ucf_cal(grp)
    assert all([v for v in sched.values()])

    wday, room = sched["wday"], sched["room"]

    # generate meeting dates, on a weekly basis
    mtg_dts = Series(dt_range)[(((offset - 1) * 7) + __day2idx(wday))::7]
    # remove the holidays
    mtg_dts = mtg_dts[~mtg_dts.isin(dt_holis)]

    time_s, time_e = sched["time"].split("-")
    mtg_time = Timedelta(hours=int(time_s[:2]), minutes=int(time_s[3:]))
    mtg_dts += mtg_time
    
    log.info("Meeting dates:\n%s", mtg_dts)

    sched = [MeetingMeta(to_datetime(mtg), room) for mtg in mtg_dts]
    log.debug(sched)

    return sched


def __can_overwrite(path: Path) -> bool:
    s = f"I see that `{path}` already exists... :/ Shall I overwrite it? [y/N] "
    if path.exists():
        return input(s).lower() != "y"


def __make_notebook(grp: Group, mtg: Meeting, auto_overwrite: bool = False) -> None:
    path = grp.as_dir() / mtg.as_nb()
    if not auto_overwrite and not __can_overwrite(path):
        return

    Path(path.parent).mkdir(exist_ok=True)

    nb = nbf.v4.new_notebook()
    nb["metadata"] = meeting.metadata(mtg)
    nb["cells"].append(meeting.heading(mtg, str(grp.as_dir())))

    with open(path, "w") as f_nb:
        nbf.write(nb, f_nb)


def __prepares_post(grp: Group, mtg: Meeting, auto_overwrite: bool = False) -> None:
    path = SITE_CONTENT_DIR / grp.as_dir(for_jekyll=True) / "_posts" / repr(mtg)
    if not auto_overwrite and not __can_overwrite(path):
        return

    path.mkdir(exist_ok=True)
    __make_posts(grp, mtg)


def __make_posts(grp: Group, mtg: Meeting) -> None:
    export = nbc.HTMLExporter()
    export.template_file = "basic"
    # TODO: implement LaTeX parser and get TPL to extract content below
    # export = nbc.LatexExporter()
    # export.template_path = [f"{res_dir}/templates/notebooks"]
    # export.template_file = f"{res_dir}/templates/notebooks/nb-as-post.tpl"
    
    try:
        nb = nbf.read(f"{grp.as_dir() / mtg.as_nb()}", as_version=4)
    except FileNotFoundError:
        __make_notebook(grp, mtg)

    nb = nbf.read(f"{grp.as_dir() / mtg.as_nb()}", as_version=4)
    
    sigai = nb["metadata"]["ucfai"]
    
    idx = next((idx
                for idx, cell in enumerate(nb["cells"])
                if cell["metadata"]["type"] == "sigai_heading")
               , None)
    
    del nb["cells"][idx]
    
    body, _ = export.from_notebook_node(nb)
    
    output = Path(f"{SITE_CONTENT_DIR}/{grp.as_dir(for_jekyll=True)}/_posts/"
                  f"{repr(mtg)}/{repr(mtg)}.md")
    output.touch()
    
    with open(output, "w") as f:
        f.write("---\n")
        f.write(f"title: \"{sigai['title']}\"\n")
        f.write(f"categories: [\"{grp.sem.short}\"]\n")
        # f.write(f"tags: {[sigai['name']]}\n")
        f.write(f"authors: {[_['github'] for _ in sigai['authors']]}\n")
        f.write(f"description: >-\n  \"{sigai['description']}\"\n")
        f.write("---\n")
        f.write(body)
    

def __make_banner(grp: Group, mtg: Meeting) -> None:
    """Generates the banner for each meeting."""
    log.debug(f"Generating `banner.jpg` for {repr(mtg)}...")

    # region meta, needed to generate the banner and restrict images
    tpl_banner = Template(open(res_dir / "templates/event-banner.html").read())

    accepted_content_types = list(map(
        lambda x: f"image/{x}", ["jpeg", "png", "gif", "tiff"]
    ))
    # endregion

    ext = mtg.covr.split(".")[-1]
    cvr_pth = Path(f"{SITE_CONTENT_DIR}/{grp.as_dir(for_jekyll=True)}/_posts/{repr(mtg)}/cover.{ext}")
    if mtg.covr:
        # region snag banner image from url
        # TODO: Make robust to detecting Image Format, don't rely on File Ext...
        cvr = requests.get(mtg.covr, headers={"user-agent": "Mozilla/5.0"})
        if cvr.headers["Content-Type"] in accepted_content_types:
            img_bytes = io.BytesIO(cvr.content)
            try:
                # noinspection PyTypeChecker
                cvr_bytes = io.BytesIO(open(cvr_pth, "rb").read())
    
                # get hashes to check for diff
                # img_hash = hashlib.sha256(img_bytes).hexdigest()
                # cvr_hash = hashlib.sha256(cvr_bytes).hexdigest()
                #
                # if cvr_hash != img_hash:
                #     img = Image.open(img_bytes)
                #     img.save(cvr_pth)
            except FileNotFoundError:
                img = Image.open(img_bytes)
                img.save(cvr_pth)
        # endregion

    # region render the banner and save
    out = cvr_pth.with_name("banner.jpg")

    banner = tpl_banner.render(
        date=mtg.meta.date,
        room=mtg.meta.room,
        name=mtg.name.encode("ascii", "xmlcharrefreplace").decode("utf-8"),
        cover=cvr_pth.absolute() if mtg.covr else ""
    )
    
    imgkit.from_string(banner, out, options={"quiet": ""})
    # endregion

# endregion
