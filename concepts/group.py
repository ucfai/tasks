import logging
from typing import Any

from .semester import Semester

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# https://pyyaml.org/wiki/PyYAMLDocumentation#constructors-representers-resolvers
class Group:
    def __init__(self, name: str, sem_meta: Semester) -> None:
        self.name = name
        self.semester = sem_meta
        self.coords = None
        self.push_kaggle = True
        self.make_notebooks = True
        self.fileno = ""
        self.keys = ""

    def __str__(self) -> str:
        return self.name.lower().replace(" ", "-")

    def __repr__(self) -> str:
        return f"{self.name} Group"

    def __setattr__(self, key, value) -> None:
        self.__dict__[key] = value

    def __getattr__(self, item) -> Any:
        # assert item in self.__dict__, (item, self.__dict__)
        return self.__dict__[item]


class Core(Group):
    def __init__(self, semester_shortname: str):
        assert len(semester_shortname) == 4
        super().__init__("core", Semester(shortname=semester_shortname))
