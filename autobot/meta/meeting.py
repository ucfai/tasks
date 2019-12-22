import io
import os
import copy
import datetime
import shutil
import subprocess
from pathlib import Path
from hashlib import sha256
from typing import List, Dict
from itertools import product
from distutils.dir_util import copy_tree

import imgkit
import requests
import yaml
from PIL import Image
import pandas as pd
from jinja2 import Template
import nbformat as nbf
import nbconvert as nbc
from nbgrader.preprocessors import ClearSolutions, ClearOutput

from autobot import ORG_NAME

from . import MeetingMeta
from .coordinator import Coordinator
from .group import Group

src_dir = Path(__file__).parent.parent


class Meeting:
    def __init__(self, group: Group, meeting_dict: Dict, meta: MeetingMeta):
        assert set(["required", "optional"]).intersection(set(meeting_dict.keys()))

        self.group = group
        self.required = meeting_dict["required"]
        self.optional = meeting_dict["optional"]

        if "date" in self.optional and self.optional["date"]:
            date = self.optional["date"]
        else:
            date = meta.date

        if "room" in self.optional and self.optional["room"]:
            room = self.optional["room"]
        else:
            room = meta.room

        self.meta = MeetingMeta(date, room)

        self.required["instructors"] = [x.lower() for x in self.required["instructors"]]

        for key in self.required.keys():
            assert self.required[
                key
            ], f"You haven't specified `{key}` for this meeting..."

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
