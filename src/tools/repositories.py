from pathlib import Path

from .. import config
from ..concepts import Group, Meeting

_org_name = config["org_name"]

REMOTE_CONTENT_SITE = config["apis"]["version-control"]["platform"]
REMOTE_CONTENT_ROOT = config["apis"]["version-control"]["repo_owner"]


def local_group_root(ctx):
    return Path(repr(ctx["group"]))


def local_semester_root(ctx):
    return local_group_root(ctx) / repr(ctx["semester"])


def local_meeting_root(ctx, m: Meeting):
    return local_semester_root(ctx) / repr(m)


def remote_group_root(group: Group) -> str:
    return "/".join([REMOTE_CONTENT_ROOT, repr(group)])


def remote_semester_root(m: Meeting, branch: str = "master") -> str:
    return f"{remote_group_root(m.group)}/tree/{branch}/{m.group.semester}"
    # return "/".join(
    #     [
    #         remote_group_root(m.group),  # Git URL
    #         "tree",  # "Git Tree" - we're looking at a filetree
    #         branch,  # Branch Name
    #         m.group.semester,  # Semester's "shortname," e.g. fa19
    #     ]
    # )


def remote_meeting_root(meeting: Meeting) -> str:
    return "/".join(
        [
            remote_semester_root(meeting),  # Git URL semeseter root
            repr(meeting),  # meeting path
        ]
    ).replace(
        "tree", "blob"
    )  # we're looking at a "Git Blob" instead of a "Git Tree"
