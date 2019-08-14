import hashlib
import io
from pathlib import Path
from typing import List, Dict

import nbformat as nbf
from jinja2 import Template

from autobot.meta import MeetingMeta
from autobot.meta.coordinator import Coordinator

src_dir = Path(__file__).parent.parent


class Meeting:
    def __init__(self, name: str, file: str, covr: str, meta: MeetingMeta,
                 inst: List[Coordinator], desc: str, tags: List[str], **kwargs):
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

    def fq_path(self, group):
        return group.as_dir() / self.meta.sem / self.as_dir()

    def as_post(self):
        # currently setup for Jekyll
        # TODO: move support to Hugo
        return Path(self.meta.sem) / self.as_md()

    def as_md(self): return self.__as_path(ext="md")

    def as_nb(self): return self.__as_path(ext="ipynb")

    def as_dir(self): return self.__as_path(ext="")

    def __as_path(self, ext: str = ""):
        if ext and "." != ext[0]:
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


def metadata(meeting: Meeting) -> Dict:
    return {
        "autobot": {
            "authors": [c.as_metadata() for c in meeting.inst],
            "description": meeting.desc.strip(),
            "title": meeting.name,
            "date": meeting.meta.date.isoformat()[:10],  # outputs as 2018-01-16
            "tags": [],
        }
    }


def heading(meeting: Meeting, group: str) -> nbf.NotebookNode:
    tpl_heading = Template(
        open(src_dir / "templates/notebooks/nb-heading.html").read())
    tpl_args = {
        "group_sem": group,
        "authors": meeting.inst,
        "title": meeting.name,
        "file": meeting.file,
        "date": meeting.meta.date.isoformat()[:10]
    }

    rendering = tpl_heading.render(**tpl_args)
    head_meta = {"name": meeting.name, "major_heading": True}
    return nbf.v4.new_markdown_cell(rendering, metadata=head_meta)
