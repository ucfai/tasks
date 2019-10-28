import io
import os
import sys
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
from tqdm import tqdm

from autobot.meta import Group, Meeting, Coordinator
from autobot.lib.apis import ucf, kaggle
from autobot.lib.utils import meetings, paths


def semester_setup(group: Group) -> None:
    """Sets up the skeleton for a new semester.
    1. Copies base `yml` into `<group>/<semester>/`
    2. Sets up the Website's entires for the given semester. (NB: Does **not**
       make posts.)
    3. Performs a similar setup with Google Drive & Google Forms.
    4. Generates skeleton for the login/management system.
    """
    if paths.repo_group_folder(group).exists():
        log.warning(f"{paths.repo_group_folder(group)} exists! Tread carefully.")
        overwrite = input(
            "The following actions **are destructive**. " "Continue? [y/N] "
        )
        if overwrite.lower() not in ["y", "yes"]:
            return

    # region 1. Copy base `yml` files.
    #   1. env.yml
    #   2. overhead.yml
    #   3. syllabus.yml
    # strong preference to use `shutil`, but can't use with existing dirs
    # shutil.copytree("autobot/templates/seed/meeting", path.parent)
    copy_tree("autobot/templates/seed/group", str(paths.repo_group_folder(group)))

    env_yml = paths.repo_group_folder(group) / "env.yml"
    env = Template(open(env_yml, "r").read())

    with open(env_yml, "w") as f:
        f.write(env.render(org_name=ORG_NAME, group=group))
    # endregion

    # region 2. Setup Website for this semester
    paths.site_group_folder(group)
    # endregion

    # region 3. Setup Google Drive & Google Forms setup
    # TODO: make Google Drive folder for this semester
    # TODO: make "Sign-Up" Google Form and Google Sheet
    # TODO: make "Sign-In" Google Form and Google Sheet
    # endregion


def semester_upkeep(group: Group, forced_overwrite: bool = False) -> None:
    """Assumes a [partially] complete Syllabus; this will only create new
    Syllabus entries' resources - thus avoiding potentially irreversible
    changes/deletions).

    1. Reads `overhead.yml` and parses Coordinators
    2. Reads `syllabus.yml`, parses the Semester's Syllabus, and sets up
       Notebooks
    """
    # region Read `overhead.yml` and seed Coordinators
    # noinspection PyTypeChecker
    overhead = yaml.load(open(paths.repo_group_folder(group) / "overhead.yml", "r"))
    coordinators = overhead["coordinators"]
    setattr(group, "coords", Coordinator.parse_yaml(coordinators))

    overhead = overhead["meetings"]
    meeting_schedule = ucf.make_schedule(group, overhead)
    # endregion

    # region 2. Read `syllabus.yml` and parse Syllabus
    syllabus_yml = yaml.load(open(paths.repo_group_folder(group) / "syllabus.yml", "r"))

    syllabus = []
    for meeting, schedule in tqdm(
        zip(syllabus_yml, meeting_schedule), desc="Parsing Meetings"
    ):
        try:
            syllabus.append(Meeting(group, meeting, schedule))
        except AssertionError:
            tqdm.write(
                "You're missing `required` fields from the meeting "
                f"happening on {schedule.date} in {schedule.room}!"
            )
            continue

    for meeting in tqdm(syllabus, desc="Building/Updating Meetings", file=sys.stdout):
        tqdm.write(f"{repr(meeting)} ~ {str(meeting)}")

        # Perform initial directory checks/clean-up
        meetings.update_or_create_folders_and_files(meeting)

        # Make edit in the group-specific repo
        meetings.update_or_create_notebook(meeting, overwrite=forced_overwrite)
        meetings.download_papers(meeting)
        kaggle.push_kernel(meeting)

        # Make edits in the ucfai.org repo
        meetings.render_banner(meeting)
        # meetings.render_instagram_post(meeting)
        meetings.export_notebook_as_post(meeting)
    # endregion


# region Accepted Operations
ACCEPTED = {"semester-setup": semester_setup, "semester-upkeep": semester_upkeep}
# endregion
