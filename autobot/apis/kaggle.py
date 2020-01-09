import os
import subprocess
from pathlib import Path

from tqdm import tqdm

from autobot import ORG_NAME
from autobot.utils import paths
from autobot.meta.meeting import Meeting

KAGGLE_USERNAME = "ucfaibot"
KAGGLE_CONFIG_DIR = Path(__file__).parent.parent.parent


def _configure_environment() -> None:
    if "KAGGLE_CONFIG_DIR" not in os.environ:
        os.environ["KAGGLE_CONFIG_DIR"] = str(KAGGLE_CONFIG_DIR)
    elif "KAGGLE_CONFIG_DIR" in os.environ and os.environ["KAGGLE_CONFIG_DIR"] != str(
        KAGGLE_CONFIG_DIR
    ):
        tqdm.write(f"Found `KAGGLE_CONFIG_DIR = {os.environ['KAGGLE_CONFIG_DIR']}`")


def pull_kernel(meeting: Meeting) -> None:
    _configure_environment()

    cwd = os.getcwd()
    os.chdir(paths.tmp_meeting_folder(meeting))
    subprocess.call(
        f"kaggle k pull -wp {KAGGLE_USERNAME}/{slug_kernel(meeting)}", shell=True
    )
    os.chdir(cwd)


def diff_kernel(meeting: Meeting) -> bool:
    _configure_environment()
    pull_kernel(meeting)

    cwd = os.getcwd()
    # TODO compute sha256 over the meeting's Workbook and what we pulled from Kaggle, compare the hexdigests


def push_kernel(meeting: Meeting) -> None:
    _configure_environment()

    if diff_kernel(meeting):
        cwd = os.getcwd()
        os.chdir(paths.repo_meeting_folder(meeting))
        subprocess.call("kaggle k push", shell=True)
        os.chdir(cwd)
    else:
        tqdm.write("Kernels are the same. Skipping.")


def slug_kernel(meeting: Meeting) -> str:
    """Generates Kaggle Kernel slugs of the form: `<group>-<semester>-<filename>`
    e.g. if looking at the Fall 2019 Computational Cognitive Neuroscience
    lecture, the slug would be: `core-fa19-ccn`."""
    return (
        f"{repr(meeting.group)}-{meeting.group.semester.short}-"
        f"{meeting.required['filename']}"
    )


def slug_competition(meeting: Meeting) -> str:
    """Since Kaggle InClass competitions are listed under general competitions,
    we take the `slug_kernel` of the meeting, and prepend `ORG_NAME`, which
    for AI@UCF, would be `ucfai`."""
    return f"{ORG_NAME}-{slug_kernel(meeting)}"
