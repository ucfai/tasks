from pathlib import Path

from autobot.concepts import Group

CONTENT_ROOT = Path("groups")


def group_root(group: Group):
    return CONTENT_ROOT / repr(group)


def semester_root(meeting: Meeting):
    return group_root(meeting.group) / meeting.semester.shortname
