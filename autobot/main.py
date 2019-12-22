from argparse import ArgumentParser
from datetime import datetime as dt
from distutils.dir_util import copy_tree
from itertools import product
from pathlib import Path
from typing import List, Dict
import datetime
import hashlib
import io
import logging
import os
import shutil
import sys

from jinja2 import Template
from PIL import Image
from tqdm import tqdm
import argcomplete
import imgkit
import nbconvert as nbc
import nbformat as nbf
import pandas as pd
import requests
import requests
import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from autobot import safety, get_template, ORG_NAME
from autobot.apis import ucf, kaggle
from autobot.meta import Group, Meeting, Coordinator, groups
from autobot.utils import meetings, paths


def main():
    logging.basicConfig()

    semester = ucf.determine_semester().short

    parser = ArgumentParser(prog="autobot")
    parser.add_argument("group", choices=groups.ACCEPTED.keys())
    parser.add_argument("semester", nargs="?", default=semester)

    action = parser.add_subparsers(title="action", dest="action")

    setup = action.add_parser("semester-setup")

    upkeep = action.add_parser("semester-upkeep")

    which_mtgs = upkeep.add_mutually_exclusive_group(required=True)
    which_mtgs.add_argument("-d", "--date", type=str, help="date format: MM/DD")
    which_mtgs.add_argument(
        "-n", "--name", type=str, help="name format: <filename> - `from syllabus.yml`"
    )
    which_mtgs.add_argument("--all", action="store_true")

    parser.add_argument("--overwrite", action="store_true")

    argcomplete.autocomplete(parser)

    args = parser.parse_args()
    args.semester = ucf.semester_converter(short=args.semester)

    # `groups.ACCEPTED` makes use of Python's dict-based execution to allow for
    #   restriction to one of the Groups listed in `meta/groups.py`
    group = groups.ACCEPTED[args.group](args.semester)

    safety.force_root()

    if args.action == "semester-setup":
        semester_setup(group)
    elif args.action == "semester-upkeep":
        if args.all:
            semester_upkeep_all(group, overwrite=args.overwrite)
        else:
            meetings = _parse_and_load_meetings(group)

            meeting = None
            if args.date:
                meeting = next((m for m in meetings if args.date in repr(m)), None)
            elif args.name:
                meeting = next((m for m in meetings if args.name in repr(m)), None)

            if meeting is None:
                raise ValueError("Couldn't find the meeting you were looking for!")

            semester_upkeep(meeting, overwrite=args.overwrite)


def semester_setup(group: Group) -> None:
    """Sets up the skeleton for a new semester.
    1. Copies base `yml` into `<group>/<semester>/`
    2. Sets up the Website's entires for the given semester. (NB: Does **not**
       make posts.)
    3. Performs a similar setup with Google Drive & Google Forms.
    4. Generates skeleton for the login/management system.
    """
    if paths.repo_group_folder(group).exists():
        logging.warning(f"{paths.repo_group_folder(group)} exists! Tread carefully.")
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
    copy_tree(get_template("seed/group"), str(paths.repo_group_folder(group)))

    env_yml = paths.repo_group_folder(group) / "env.yml"
    env = Template(open(env_yml, "r").read())

    with open(env_yml, "w") as f:
        f.write(
            env.render(
                org_name=ORG_NAME, group_name=repr(group), semester=group.semester.short
            )
        )
    # endregion

    # region 2. Setup Website for this semester
    paths.site_group_folder(group)
    # endregion

    # region 3. Setup Google Drive & Google Forms setup
    # TODO: make Google Drive folder for this semester
    # TODO: make "Sign-Up" Google Form and Google Sheet
    # TODO: make "Sign-In" Google Form and Google Sheet
    # endregion

    # region 4. Setup YouTube Semester Playlist
    # TODO: create YouTube playlist
    # endregion


def _parse_and_load_meetings(group: Group):
    # region Read `overhead.yml` and seed Coordinators
    # noinspection PyTypeChecker
    overhead_yml = paths.repo_group_folder(group) / "overhead.yml"
    overhead_yml = yaml.load(open(overhead_yml, "r"), Loader=Loader)
    coordinators = overhead_yml["coordinators"]
    setattr(group, "coords", Coordinator.parse_yaml(coordinators))

    meeting_overhead = overhead_yml["meetings"]
    meeting_schedule = ucf.make_schedule(group, meeting_overhead)
    # endregion

    # region 2. Read `syllabus.yml` and parse Syllabus
    syllabus_yml = paths.repo_group_folder(group) / "syllabus.yml"
    syllabus_yml = yaml.load(open(syllabus_yml, "r"), Loader=Loader)

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

    return syllabus


def semester_upkeep(meeting: Meeting, overwrite: bool = False) -> None:
    tqdm.write(f"{repr(meeting)} ~ {str(meeting)}")

    # Perform initial directory checks/clean-up
    meetings.update_or_create_folders_and_files(meeting)

    # Make edit in the group-specific repo
    meetings.update_or_create_notebook(meeting, overwrite=overwrite)
    # meetings.download_papers(meeting)
    # kaggle.push_kernel(meeting)

    # Make edits in the ucfai.org repo
    # meetings.render_banner(meeting)
    # meetings.render_instagram_post(meeting)
    # meetings.export_notebook_as_post(meeting)

    # Video Rendering and such
    # videos.dispatch_recording(meeting)  # unsure that this is needed

    # videos.render_banner(meeting)

    # this could fire off a request to GCP to avoid long-running
    # videos.compile_and_render(meeting)

    # youtube.upload(meeting)


def semester_upkeep_all(group: Group, overwrite: bool = False) -> None:
    """Assumes a [partially] complete Syllabus; this will only create new
    Syllabus entries' resources - thus avoiding potentially irreversible
    changes/deletions).

    1. Reads `overhead.yml` and parses Coordinators
    2. Reads `syllabus.yml`, parses the Semester's Syllabus, and sets up
       Notebooks.
    """
    syllabus = _parse_and_load_meetings(group)

    for meeting in tqdm(syllabus, desc="Building/Updating Meetings", file=sys.stdout):
        semester_upkeep(meeting, overwrite=overwrite)
