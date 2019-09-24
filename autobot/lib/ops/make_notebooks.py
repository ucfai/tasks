import io
import os
import datetime
from pathlib import Path
from typing import List, Dict

import imgkit
import requests
import yaml
from PIL import Image
import pandas as pd
from jinja2 import Template
import nbformat as nbf
import nbconvert as nbc

from autobot.meta import meeting, Coordinator, Group, Meeting
from autobot.lib import safety
from autobot.lib.configs import website
from autobot.lib.apis import ucf


ACCEPTED_ITEMS = set(["notebook", "post", "banner"])


def make_notebooks(group: Group, auto_overwrite: bool = False) -> None:
    """Assumes a [partially] complete Syllabus; this will only create new
    Syllabus entries' resources - thus avoiding potentially irreversible
    changes/deletions).

    1. Reads `overhead.yml` and parses Coordinators
    2. Reads `syllabus.yml`, parses the Semester's Syllabus, and sets up
       Notebooks
    """
    safety.force_root()

    # region Read `overhead.yml` and seed Coordinators
    # noinspection PyTypeChecker
    overhead = yaml.load(open(group.as_dir() / "overhead.yml", "r"))
    coordinators = overhead["coordinators"]
    setattr(group, "coords", Coordinator.parse_yaml(coordinators))

    meetings = overhead["meetings"]
    # endregion

    # region 2. Read `syllabus.yml` and parse Syllabus
    syllabus = yaml.load(open(group.as_dir() / "syllabus.yml", "r"))
    _meeting_offset = meetings["start_offset"]

    _parse_and_make_meetings("primary", group, meetings, syllabus,
                             _meeting_offset)

    _parse_and_make_meetings("supplementary", group, meetings, syllabus,
                             _meeting_offset + 1)
    # endregion

def _parse_and_make_meetings(key: str, group: Group, meetings: Dict, syllabus: list,
                           offset: int) -> None:
    """Parses the meetings and generates the necessary skeleton."""
    try:
        meeting_days = meetings[key]
        syllabus = syllabus[key]
    except KeyError:
        log.warning(f"No `{key}` in the `overhead.yml` or `syllabus.yml`...")
        return

    meeting_sched = ucf.make_schedule(group, meeting_days, offset)

    meetings = [Meeting(**Meeting.parse_yaml(mtg, group.coords, meta))
                for mtg, meta in zip(syllabus, meeting_sched)]

    setattr(group, f"sched_{key}", meeting_sched)

    funcs = [_make_notebook, _prepare_post, _make_banner]
    for meeting in meetings:
        for func in funcs:
            if _can_overwrite(meeting, str(func)):
                func(group, meeting, True)
            elif auto_overwrite and meeting.meta.date > today:
                func(group, meeting, auto_overwrite)

    return


def _can_overwrite(meeting: Meeting = None, item: str = None):
    assert (meeting and item) or path, \
        "`meeting` and `item` must be specified or `path` only."

    if (meeting and item):
        assert item in ACCEPTED_ITEMS or item is None

        s = (f"It seems like you're attempting to overwrite a passed meeting. "
             f"Do you wish to continute? [y/N] ")
    elif path:
        s = (f"It seems like `{path}` already exists... Do you want to overwrite"
             f"it? [y/N]")
        if not path.exists():
            return True
    else:
        raise ValueError("Check calls for `_can_overwrite`, something is wrong...")

    v = input(s).lower()

    return v in ["y", "yes"]


def _make_notebook(group: Group, meeting: Meeting, auto_overwrite: bool) -> None:
    path = group.as_dir() / meeting.as_dir()

    if not auto_overwrite:
        return

    Path(path.parent).mkdir()

    nb = nbf.v4.new_notebook()
    nb["metadata"] = Meeting.metadata(meeting)
    nb["cells"].append(Meeting.heading(meeting, str(group.as_dir())))

    with open(path, "w") as f_nb:
        nbf.write(nb, f_nb)


def _prepare_post(group: Group, meeting: Meeting, auto_overwrite: bool) -> None:
    path = website.CONTENT_DIR / group.as_dir(for_hugo=True) / "_posts" / repr(meeting)
    if not auto_overwrite:
        return

    path.mkdir()

    # TODO: implement LaTeX parser and get TPL to extract content below
    export = nbc.MarkdownExporter()
    export.template_path = [f"{res_dir}/templates/notebooks"]
    export.template_file = "nb-as-post"

    try:
        nb = nbf.read(f"{group.as_dir()} / {meeting.as_nb()}", as_version=4)
    except FileNotFoundError:
        _make_notebook(group, meeting, auto_overwrite=auto_overwrite)
        nb = nbf.read(f"{group.as_dir()} / {meeting.as_nb()}", as_version=4)

    autobot = nb["metadata"]["autobot"]

    idx = next((idx for idx, cell in enumerate(nb["cells"])
                if cell["metadata"]["type"] == "autobot-heading"), None)

    del nb["cells"][idx]

    body, _ = export.from_notebook_node(nb)

    output = Path(f"{SITE_CONTENT_DIR}/{group.as_dir(for_hugo=True)}/_posts/"
                  f"{repr(meeting)}/{repr(meeting)}.md")
    with open(output, "w") as f:
        f.write(body)


def _make_banner(group: Group, meeting: Meeting, auto_overwrite: bool) -> None:
    """Generates banner for each meeting."""
    log.debug(f"Generating `banner.jpg` for {repr(meeting)}...")

    tpl_banner = Template(open(res_dir / "templates/event-banner.html", "r").read())

    accepted_content_types = list(map(
        lambda x: f"image/{x}", ["jpeg", "png", "gif", "tiff"]
    ))

    ext = meeting.covr.split(".")[-1]
    cover_img_path = (SITE_CONTENT_DIR / group.as_dir(for_hugo=True) / "_posts" /
                      repr(meeting) / "cover.jpg")

    if meeting.covr:
        # TODO: Make robust to detecting img fmt (and don't rely on file ext)
        cover = requests.get(meeting.covr, headers={"user-agent": "Mozilla/5.0"})
        if cover.headers["Content-Type"] in accepted_content_types:
            image_as_bytes = io.BytesIO(cover.content)
            try:
                # noinspection PyTypeChecker
                cover_as_bytes = io.BytesIO(open(cover_path, "rb").read())

                # get hashes to check for diff
                image_hash = hashlib.sha256(image_as_bytes).hexdigest()
                cover_hash = hashlib.sha256(cover_as_bytes).hexdigest()

                if cover_hash != image_hash:
                    image = Image.open(image_as_bytes)

            except FileNotFoundError:
                image = Image.open(img_as_bytes)

            finally:
                image.save(cover_path)

    out = cover_path.with_name("banner.jpg")

    banner = tpl_banner.render(
        date=meeting.meta.date,
        room=meeting.meta.room,
        name=meeting.meta.name,
        cover=cover_path.absolute() if meeting.cover else ""
    )

    imgkit.from_string(banner, out, options={"quiet": ""})

