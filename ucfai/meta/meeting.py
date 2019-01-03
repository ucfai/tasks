import hashlib
import io
from pathlib import Path
from typing import List, Dict

import nbformat as nbf
from jinja2 import Template

from ucfai.meta import MeetingMeta
from ucfai.meta.coordinator import Coordinator

res_dir = Path(__file__).parent


class Meeting:
    def __init__(self, name: str, file: str, covr: str, meta: MeetingMeta,
                 inst: List[Coordinator], desc: str, tags: List[str]) -> None:
        self.name, self.file = name, file
        self.covr = covr
        self.meta = meta
        self.inst = inst
        self.desc = desc
        self.nb = None
        self.tags = tags

    def write_yaml(self) -> Dict:
        """This prepares the dict to write each entry in `syllabus.yml`."""
        return {
            "name": self.name,
            "file": self.file,
            "covr": self.covr,
            "inst": self.inst,
            "desc": self.desc,
            "date": self.meta.date,
            "wday": self.meta.wday,
            "time": self.meta.time_s,
            "room": self.meta.room,
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
        reqd_keys = {"name", "file", "covr", "inst", "desc"}
        assert reqd_keys.intersection(set(d.keys())) == reqd_keys

        assert d["name"], "A lecture hasn't been named... do that first."
        assert d["file"], "Each lecture needs a `filename` for the site and " \
                          "Notebook generation."
        assert d["inst"], "It seems you haven't specified a Coordinator for " \
                          "this meeting, do that first."

        d["inst"] = list(map(lambda x: coords[x], d["inst"]))
        d["meta"] = meta

        return d

    def as_nb(self): return self.__as_path(ext=".ipynb")

    def as_dir(self): return self.__as_path(ext="")

    def __as_path(self, ext: str = ""):
        if ext and "." not in ext:
            ext = f".{ext}"
        return Path(f"{repr(self)}/{repr(self)}{ext}")

    def __repr__(self):
        if not self.meta.date:
            raise ValueError("`Meeting.date` must be defined for this to work.")
        return f"{self.meta.date.isoformat()[:10]}-{self.file}"

    def __str__(self): return self.name

    def __lt__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date < other.meta.date

    def __le__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date <= other.meta.date

    def __eq__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date == other.meta.date

    def __ge__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date >= other.meta.date

    def __gt__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date > other.meta.date


def metadata(mtg: Meeting) -> Dict:
    return {
        "ucfai": {
            "authors": [c.as_metadata() for c in mtg.inst],
            "description": mtg.desc.strip(),
            "title": mtg.name,
            "date": mtg.meta.date.isoformat()[:10],  # outputs as 2018-01-16
        }
    }


def heading(mtg: Meeting, group: str) -> nbf.NotebookNode:
    tpl_heading = Template(
        open(res_dir / "templates" / "nb-heading.html").read())
    tpl_args = {
        "group_sem": repr(group),
        "authors": mtg.inst,
        "title": mtg.name,
        "file": mtg.file,
        "date": mtg.meta.date.isoformat()[:10]
    }

    rendering = tpl_heading.render(**tpl_args)
    head_meta = {"name": mtg.name, "type": "sigai_heading"}
    return nbf.v4.new_markdown_cell(rendering, metadata=head_meta)
