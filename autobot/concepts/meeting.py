import copy
import datetime as dt
import io
import os
import shutil
import subprocess
from distutils.dir_util import copy_tree
from hashlib import sha256
from itertools import product
from pathlib import Path
from typing import Dict, List

import imgkit
import nbconvert as nbc
import nbformat as nbf
import pandas as pd
import requests
import yaml
from jinja2 import Template
from nbgrader.preprocessors import ClearOutput, ClearSolutions
from PIL import Image

from . import MeetingMeta
from .coordinator import Coordinator
from .group import Group

src_dir = Path(__file__).parent.parent


# https://pyyaml.org/wiki/PyYAMLDocumentation#constructors-representers-resolvers
class Meeting:
    def __init__(
        self,
        group: Group,
        meeting_dict: Dict,
        tmpname: str = None,
        meta: MeetingMeta = None,
    ):
        assert set(["required", "optional"]).intersection(set(meeting_dict.keys()))
        self.number = 0
        if tmpname:
            self.number = int(tmpname.replace("meeting", ""))
        self.number += 1

        self.group = group
        self.required = meeting_dict["required"]
        self.optional = meeting_dict["optional"]

        if "date" in self.optional and self.optional["date"]:
            date = self.optional["date"]
            # mm, dd = self.optional["date"].split("-")
            # date = dt.date(int(self.group.semester.year), int(mm), int(dd))
        else:
            date = meta.date

        if "room" in self.optional and self.optional["room"]:
            room = self.optional["room"]
        else:
            room = meta.room

        self.meta = MeetingMeta(pd.to_datetime(date), room)

        self.required["instructors"] = [x.lower() for x in self.required["instructors"]]

        self.required["filename"] = self.required["filename"] or tmpname
        self.required["title"] = self.required["title"] or tmpname

        # for key in self.required.keys():
        #    assert self.required[
        #        key
        #    ], f"You haven't specified `{key}` for this meeting..."

    def write_yaml(self) -> Dict:
        """This prepares the dict to write each entry in `syllabus.yml`."""
        return {
            "required": {
                "title": self.title,
                "cover": self.cover,
                "filename": self.filename,
                "instructors": self.instructors,
                "datasets": self.datasets,
                "description": self.description,
            },
            "optional": {
                "date": self.meta.date,
                "room": self.meta.room,
                "tags": self.tags,
                "slides": self.slides,
                "kernels": self.kernels,
                "papers": self.papers,
            },
        }

    @staticmethod
    def parse_yaml(d: Dict, coords: Dict, meta: MeetingMeta) -> Dict:
        """This method consumes a dict which will be used to see a given
        `Meeting` instance, thus allowing for usage elsewhere.

        :param d: Dict
        :param coords: Dict
        :param meta: MeetingMeta

        :return Dict
        """
        for k, v in d["required"].items():
            assert v, f"You haven't specified `{k}` in one of the syllabi entries..."

        d["required"]["instructors"] = list(
            map(lambda x: coords[x.lower()], d["required"]["instructors"])
        )
        d["meta"] = meta

        if d["optional"]["room"]:
            d["meta"]["room"] = d["optional"]["room"]

        if d["optional"]["date"]:
            d["meta"]["date"] = d["optional"]["date"]

        return d

    def __as_path(self, ext: str = ""):
        if ext and "." != ext[0]:
            ext = f".{ext}"
        return Path(f"{repr(self)}/{repr(self)}{ext}")

    def __repr__(self):
        if not self.meta.date:
            raise ValueError("`Meeting.date` must be defined for this to work.")
        return f"{self.meta.date.isoformat()[:10]}-{self.required['filename']}"

    def __str__(self):
        return self.required["title"]

    def __lt__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date < other.meta.date

    def __le__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date <= other.meta.date

    def __ge__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date >= other.meta.date

    def __gt__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date > other.meta.date

    def __eq__(self, other) -> bool:
        if type(other) is Meeting:
            return repr(self) == repr(meeting)
        elif type(other) in [Path, str]:
            return
