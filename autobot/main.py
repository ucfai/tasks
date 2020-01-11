from argparse import ArgumentParser
from distutils.dir_util import copy_tree
from pathlib import Path
from typing import List, Dict
import logging
import os
import sys

from jinja2 import Template
from tqdm import tqdm

from autobot import safety, get_template, ORG_NAME
from autobot.apis import kaggle, ucf
from autobot.meta import Group, Meeting, Coordinator, groups
from autobot.utils import meetings, paths, syllabus


def main():
    logging.basicConfig()

    semester = ucf.determine_semester().short

    parser = ArgumentParser(prog="autobot")
    parser.add_argument("group", choices=groups.ACCEPTED.keys())
    parser.add_argument("semester", nargs="?", default=semester)
    if "IN_DOCKER" in os.environ:
        parser.add_argument("--wait", action="store_true")

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

    args = parser.parse_args()

    if "IN_DOCKER" in os.environ and args.wait:
        import time

        print("Waiting...")
        while True:
            time.sleep(1)

    args.semester = ucf.semester_converter(short=args.semester)

    # `groups.ACCEPTED` makes use of Python's dict-based execution to allow for
    #   restriction to one of the Groups listed in `meta/groups.py`
    group = groups.ACCEPTED[args.group](args.semester)

    safety.force_root()

    if args.action == "semester-setup":
        semester_setup(group)
    elif args.action == "semester-upkeep":
        meetings = syllabus.parse(group)
        if not args.all:
            meeting = None
            if args.date:
                meeting = next((m for m in meetings if args.date in repr(m)), None)
            elif args.name:
                meeting = next((m for m in meetings if args.name in repr(m)), None)

            if meeting is None:
                raise ValueError("Couldn't find the meeting you were looking for!")

            meetings = [meeting]  # formats so semester upkeep accepts

        semester_upkeep(meetings, overwrite=args.overwrite)


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


def semester_upkeep(meetings: List[Meeting], overwrite: bool = False) -> None:
    """Assumes a [partially] complete Syllabus; this will only create new
    Syllabus entries' resources - thus avoiding potentially irreversible
    changes/deletions).

    1. Reads `overhead.yml` and parses Coordinators
    2. Reads `syllabus.yml`, parses the Semester's Syllabus, and sets up
       Notebooks.
    """
    for meeting in tqdm(meetings, desc="Building / Updating Meetings", file=sys.stdout):
        tqdm.write(f"{repr(meeting)} ~ {str(meeting)}")

        # Perform initial directory checks/clean-up
        # meetings.update_or_create_folders_and_files(meeting)

        # Make edit in the group-specific repo
        # meetings.update_or_create_notebook(meeting, overwrite=overwrite)
        # meetings.download_papers(meeting)
        kaggle.push_kernel(meeting)

        # Make edits in the ucfai.org repo
        # banners.render_cover(meeting)
        # banners.render_weekly_instagram_post(meeting)  # this actually needs a more global setting
        # meetings.export_notebook_as_post(meeting)

        # Video Rendering and Upload
        # videos.dispatch_recording(meeting)  # unsure that this is needed
        # banners.render_video_background(meeting)
        # this could fire off a request to GCP to avoid long-running local renders
        # videos.compile_and_render(meeting)
        # videos.upload(meeting)
