import logging
from pathlib import Path
from typing import Any

from ucfai.meta import SemesterMeta

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Group:

    work_dir: Path = ""

    @staticmethod
    def workdir(path: str, file: str) -> Path:
        """Returns the working directory for this Group during the given
        semester, with the Meeting Path and particular file appended.

        :param path: str
        :param file: str

        :return: Path
        """
        return Group.work_dir / path / file

    def __init__(self, name: str, sem_meta: SemesterMeta) -> None:
        self.name = name
        self.sem = sem_meta
        self.coords = None
        self.prim_mtgs = None
        self.supp_mtgs = None
        Group.work_dir = self.as_dir()

    def __str__(self) -> str:
        return f"{self.name} Group"

    def __repr__(self) -> str:
        return self.name.lower().replace(" ", "-")

    def __setattr__(self, key, value) -> None:
        self.__dict__[key] = value

    def __getattr__(self, item) -> Any:
        assert item in self.__dict__.keys()
        return self.__dict__[item]

    def as_dir(self) -> Path:
        return Path(repr(self)) / self.sem.short

