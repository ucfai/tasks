from collections import namedtuple

MeetingMeta = namedtuple("MeetingMeta", ["date", "room"])

from .semester import Semester
from .group import Group
from .meeting import Meeting
from .coordinator import Coordinator

__all__ = ["Meeting", "Groups", "Coordinator", "Semester", "MeetingMeta"]
