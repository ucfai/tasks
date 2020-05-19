from typing import List
from pathlib import Path


import pandas as pd


long2short = {"fall": "fa", "summer": "su", "spring": "sp"}
# invert `long2short`
short2long = {k: v for v, k in long2short.items()}


# TODO convert Syllabus into a YAML-ready dumper
class Group:
    def __init__(
        self,
        name: str,
        semester: str,
        directors: List = [],
        coordinators: List = [],
        guests: List = [],
        startdate: str = "",
        room: str = "",
        push_kaggle: bool = True,
        make_notebooks: bool = True,
        pull_papers: bool = True,
    ):
        self.name = name
        self.room = room

        self.semester = semester
        self.startdate = str(pd.Timestamp(startdate))

        # eligible authors
        self.directors = directors
        self.coordinators = coordinators
        self.guests = guests

    def flatten(self):
        self.flattened = True

        self.startdate = pd.Timestamp(self.startdate)

        self.authors = self.directors + self.coordinators + self.guests
        return self

    def asdir(self):
        return Path(self.name) / self.semester
