from pathlib import Path

from autobot import ORG_NAME
from autobot.concepts import Group, Meeting

LOCAL_CONTENT_ROOT = Path("groups")
REMOTE_CONTENT_PLATFORM = "https://github.com"
REMOTE_CONTENT_ROOT = "/".join([REMOTE_CONTENT_PLATFORM, ORG_NAME])


def local_group_root(group: Group):
    return LOCAL_CONTENT_ROOT / repr(group)


def local_semester_root(meeting: Meeting):
    return local_group_root(meeting.group) / repr(meeting.group.semester)


def remote_group_root(group: Group):
    return "/".join([REMOTE_CONTENT_ROOT, repr(group)])


def remote_semester_root(meeting: Meeting, branch: str = "master"):
    return "/".join(
        [
            remote_group_root(meeting.group),  # Git URL
            "tree",  # "Git Tree" - we're looking at a filetree
            branch,  # Branch Name
            repr(meeting.group.semester),  # Semester's "shortname," e.g. fa19
        ]
    )


def remote_meeting_file(meeting: Meeting):
    return "/".join(
        [
            remote_semester_root(meeting),  # Git URL semeseter root
            repr(meeting),  # meeting path
            f"{ repr(meeting) }.ipynb",  # actual notebook name
        ]
    ).replace(
        "tree", "blob"
    )  # we're looking at a "Git Blob" instead of a "Git Tree"
