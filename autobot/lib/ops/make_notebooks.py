import io
import os
import datetime
import hashlib
import shutil
from distutils.dir_util import copy_tree
from pathlib import Path
from typing import List, Dict
from itertools import product

import imgkit
import requests
import yaml
from PIL import Image
import pandas as pd
from jinja2 import Template
import nbformat as nbf
import nbconvert as nbc

from autobot.meta import notebooks, Coordinator, Group, Meeting
from autobot.lib import safety
from autobot.lib.configs import website
from autobot.lib.apis import ucf

src_dir = Path(__file__).parent.parent.parent

def make_notebooks(group: Group, forced_overwrite: bool = False) -> None:
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
    _meeting_offset = meetings["start_offset"]
    meeting_sched = ucf.make_schedule(group, meetings, _meeting_offset)
    # endregion

    # region 2. Read `syllabus.yml` and parse Syllabus
    syllabus = yaml.load(open(group.as_dir() / "syllabus.yml", "r"))

    meetings = []
    for meeting, schedule in zip(syllabus, meeting_schedule):
        try:
            meetings.append(Meeting(group, meeting, schedule))
        except AssertionError:
            print("You're missing `required` fields from the meeting happening "
                  f"on {schedule.date} in {schedule.room}!")
            continue

    for meeting in meetings:
        # Make edit in the group-specific repo
        meeting.as_notebook(overwrite=forced_overwrite)
        meeting.publish_kaggle()

        # Make edits in the ucfai.org repo
        meeting.as_post(overwrite=forced_overwrite)
        meeting.as_banner(overwrite=forced_overwrite)
    # endregion
