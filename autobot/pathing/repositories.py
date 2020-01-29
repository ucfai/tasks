import os
from pathlib import Path
from typing import Union

from autobot import ORG_NAME
from autobot.concepts import Group, Meeting


LOCAL_CONTENT_ROOT = Path("groups")
if os.environ.get("IN_DOCKER", False):
    LOCAL_CONTENT_ROOT = Path("/ucfai")

REMOTE_CONTENT_PLATFORM = "https://github.com"
REMOTE_CONTENT_ROOT = "/".join([REMOTE_CONTENT_PLATFORM, ORG_NAME])


def local_group_root(group: Group) -> Path:
    return LOCAL_CONTENT_ROOT / repr(group)


def local_semester_root(meeting_or_group: Union[Group, Meeting]) -> Path:
    if isinstance(meeting_or_group, Group):
        group = meeting_or_group
    elif isinstance(meeting_or_group, Meeting):
        group = meeting_or_group.group
    else:
        raise ValueError("Didn't receive a `Meeting` or `Group`.")

    return local_group_root(group) / repr(group.semester)


def local_meeting_root(meeting: Meeting):
    return local_semester_root(meeting) / repr(meeting)


def local_meeting_file(meeting: Meeting):
    return lcoal_meeting_root(meeting) / repr(meeting)


def remote_group_root(group: Group) -> str:
    return "/".join([REMOTE_CONTENT_ROOT, repr(group)])


def remote_semester_root(meeting: Meeting, branch: str = "master") -> str:
    return "/".join(
        [
            remote_group_root(meeting.group),  # Git URL
            "tree",  # "Git Tree" - we're looking at a filetree
            branch,  # Branch Name
            repr(meeting.group.semester),  # Semester's "shortname," e.g. fa19
        ]
    )


def remote_meeting_file(meeting: Meeting) -> str:
    return "/".join(
        [
            remote_semester_root(meeting),  # Git URL semeseter root
            repr(meeting),  # meeting path
            f"{ repr(meeting) }.ipynb",  # actual notebook name
        ]
    ).replace(
        "tree", "blob"
    )  # we're looking at a "Git Blob" instead of a "Git Tree"
