from collections import namedtuple

SemesterMeta = namedtuple("SemesterMeta", ["name", "year", "short"])
MeetingMeta = namedtuple("MeetingMeta", ["date", "room"])

# this breaks PEP 8... but keeps Python from crying about forward references
from ucfai.meta.groups import *

ACCEPTED_GRP = {
    "course"      : Course,
    "data-science": DataScience,
    "intelligence": Intelligence,
    "competitions": Competitions,
}

__all__ = ["group", "groups", "coordinator", "meeting", "SemesterMeta",
           "MeetingMeta", "ACCEPTED_GRP"]
