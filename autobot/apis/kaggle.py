import json
import os
import shutil
import subprocess
from hashlib import sha256
from pathlib import Path
from typing import Union

from tqdm import tqdm
import requests

from autobot import ORG_NAME, KAGGLE_USERNAME
from autobot.actions import paths
from autobot.concepts import Meeting
from autobot.pathing import repositories

from .nbconvert import FileExtensions

KAGGLE_CONFIG_DIR = Path(__file__).parent.parent.parent
if os.environ.get("IN_DOCKER", False):
    KAGGLE_CONFIG_DIR = "/autobot"


def _configure_environment() -> None:
    if "KAGGLE_CONFIG_DIR" not in os.environ:
        os.environ["KAGGLE_CONFIG_DIR"] = str(KAGGLE_CONFIG_DIR)
    elif "KAGGLE_CONFIG_DIR" in os.environ and os.environ["KAGGLE_CONFIG_DIR"] != str(
        KAGGLE_CONFIG_DIR
    ):
        tqdm.write(f"Found `KAGGLE_CONFIG_DIR = {os.environ['KAGGLE_CONFIG_DIR']}`")


def pull_kernel(meeting: Meeting) -> Union[None, Path]:
    test_existence = requests.get(
        f"https://kaggle.com/{ KAGGLE_USERNAME }/{ slug_kernel(meeting) }"
    )

    if test_existence.status_code != requests.codes.OK:
        return None

    _configure_environment()
    subprocess.run(
        " ".join(
            [
                "kaggle k pull",
                f"-p { paths.tmp_meeting_folder(meeting) }",
                f"{KAGGLE_USERNAME}/{ slug_kernel(meeting) }",
            ]
        ),
        shell=True,
        stdout=subprocess.DEVNULL,
    )
    return (paths.tmp_meeting_folder(meeting) / slug_kernel(meeting)).with_suffix(
        FileExtensions.Workbook
    )


def local_and_remote_kernels_diff(meeting: Meeting) -> bool:
    _configure_environment()
    remote_kernel = pull_kernel(meeting)

    if not remote_kernel:
        return True

    local_kernel = repositories.local_meeting_root(meeting) / "".join(
        [repr(meeting), FileExtensions.Workbook]
    )

    remote_kernel_json = json.dumps(json.load(open(remote_kernel, "r"))).encode("utf-8")
    local_kernel_json = json.dumps(json.load(open(local_kernel, "r"))).encode("utf-8")

    remote_kernel_hash = sha256(bytes(remote_kernel_json)).hexdigest()
    local_kernel_hash = sha256(bytes(local_kernel_json)).hexdigest()

    remote_kernel.unlink()  # clean-up after diff

    return remote_kernel_hash != local_kernel_hash


def push_kernel(meeting: Meeting) -> None:
    _configure_environment()

    if local_and_remote_kernels_diff(meeting):
        subprocess.run(
            f"kaggle k push -p {paths.repo_meeting_folder(meeting)}",
            shell=True,
            # stdout=subprocess.DEVNULL,
        )
    else:
        tqdm.write("  - Kernels are the same. Skipping.")


def slug_kernel(meeting: Meeting) -> str:
    """Generates Kaggle Kernel slugs of the form: `<group>-<semester>-<filename>`
    e.g. if looking at the Fall 2019 Computational Cognitive Neuroscience
    lecture, the slug would be: `core-fa19-ccn`."""
    return "-".join(
        [
            repr(meeting.group),  # Group name
            repr(meeting.group.semester),  # Semester shortname
            meeting.required["filename"],
        ]
    )


def slug_competition(meeting: Meeting) -> str:
    """Since Kaggle InClass competitions are listed under general competitions,
    we take the `slug_kernel` of the meeting, and prepend `ORG_NAME`, which
    for AI@UCF, would be `ucfai`."""
    return "-".join([ORG_NAME, slug_kernel(meeting)])
