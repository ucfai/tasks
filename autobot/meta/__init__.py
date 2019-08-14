from collections import namedtuple

SemesterMeta = namedtuple("SemesterMeta", ["name", "year", "short"])
MeetingMeta = namedtuple("MeetingMeta", ["date", "room"])

from .group import Group
from .meeting import Meeting
from .coordinator import Coordinator

__all__ = ["groups", "coordinator", "meeting", "SemesterMeta",
           "MeetingMeta"]
