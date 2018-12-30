import hashlib
import io
from pathlib import Path
from typing import List, Dict

import nbformat as nbf

from ucfai import meeting_utils as mtg_utils
from .website import site_content_dir
from .coordinator import Coordinator

from ucfai import MeetingMeta
from .groups import Group


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

    def notebook(self):
        try:
            self.nb = nbf.read(str(self.__nb_pth()), as_version=4)
        except FileNotFoundError:
            # TODO: Need to handle not finding the expended file
            pass

        self.nb["metadata"] = mtg_utils.metadata(self)

        raise NotImplementedError()

    def make_ntbk(self, group: Group):
        path = group._to_dir() / self.__nb_pth()
        if path.exists():
            raise FileExistsError("I won't overwrite this file. :/")

        Path(path.parent).mkdir()

        nb = nbf.v4.new_notebook()
        nb["metadata"] = mtg_utils.metadata(self)
        nb["cells"].append(mtg_utils.heading(self, repr(group)))

        with open(path, "w") as f_nb:
            nbf.write(nb, f_nb)

        self.nb = nb

    def prep_post(self, group: Group):
        path = site_content_dir / group._to_dir() / str(self)
        if path.exists():
            raise FileExistsError("Erm... the entry for the site exists. :/")

        path.mkdir()

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

        assert d["inst"], "It seems you haven't specified a Coordinator for " \
                          "this meeting, do that first."

        d["inst"] = list(map(lambda x: coords[x], d["inst"]))
        d["meta"] = meta

        return d

    def __nb_pth(self):
        return self.__to_pth(ext=".ipynb")

    def __to_dir(self):
        return self.__to_pth(ext="")

    def __to_pth(self, ext: str = ""):
        if ext and "." not in ext:
            ext = f".{ext}"
        return Path(f"{self}/{self}{ext}")

    def __str__(self):
        if not self.meta.date:
            raise ValueError("`Meeting.date` must be defined for this to work.")
        return f"{self.meta.date.isoformat()[:10]}-{self.file}"

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
