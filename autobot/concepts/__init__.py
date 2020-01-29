from collections import namedtuple

MeetingMeta = namedtuple("MeetingMeta", ["date", "room"])

from .coordinator import Coordinator
from .group import Group
from .meeting import Meeting
from .semester import Semester


__all__ = ["Meeting", "Groups", "Coordinator", "Semester", "MeetingMeta"]
