import os
import subprocess
from pathlib import Path

from autobot import ORG_NAME
from autobot.lib.utils import paths
from autobot.meta.meeting import Meeting


def push_kernel(meeting: Meeting):
    # TODO: prevent Kaggle from pushing every notebook, every time
    if "KAGGLE_CONFIG_DIR" not in os.environ:
        os.environ["KAGGLE_CONFIG_DIR"] = str(Path(__file__).parent.parent.parent.parent)

    cwd = os.getcwd()
    os.chdir(paths.repo_meeting_folder(meeting))
    subprocess.call("kaggle k push", shell=True)
    os.chdir(cwd)


def slug_kernel(meeting: Meeting):
    """Generates Kaggle Kernel slugs of the form: `<group>-<semester>-<filename>`
    e.g. if looking at the Fall 2019 Computational Cognitive Neuroscience
    lecture, the slug would be: `core-fa19-ccn`."""
    return (
        f"{repr(meeting.group)}-{meeting.group.semester.short}-"
        f"{meeting.required['filename']}"
    )


def slug_competition(meeting: Meeting):
    """Since Kaggle InClass competitions are listed under general competitions,
    we take the `slug_kernel` of the meeting, and prepend `ORG_NAME`, which
    for AI@UCF, would be `ucfai`."""
    return (
        f"{ORG_NAME}-{slug_kernel(meeting)}"
    )
