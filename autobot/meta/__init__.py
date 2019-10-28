from collections import namedtuple

SemesterMeta = namedtuple("SemesterMeta", ["name", "year", "short"])
MeetingMeta = namedtuple("MeetingMeta", ["date", "room"])

from .group import Group
from .meeting import Meeting
from .coordinator import Coordinator
from . import notebooks

__all__ = ["groups", "coordinator", "SemesterMeta", "MeetingMeta", "notebooks"]
