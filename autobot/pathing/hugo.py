from pathlib import Path

from autobot.concepts import Coordinator, Group, Meeting

CONTENT_ROOT = Path("content/")


def group_root(group: Group):
    return CONTENT_ROOT / repr(group)


def semester_root(meeting: Meeting):
    return CONTENT_ROOT / repr(meeting.group) / meeting.semester.shortname


def author_root(coordinator: Coordinator):
    return CONTENT_ROOT / "authors" / coordinator.github_username
