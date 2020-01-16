import logging
from pathlib import Path
from typing import Any

from .semester import Semester

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Group:
    def __init__(self, name: str, sem_meta: Semester) -> None:
        self.name = name
        self.semester = sem_meta
        self.coords = None

    def __str__(self) -> str:
        return f"{self.name} Group"

    def __repr__(self) -> str:
        return self.name.lower().replace(" ", "-")

    def __setattr__(self, key, value) -> None:
        self.__dict__[key] = value

    def __getattr__(self, item) -> Any:
        assert item in self.__dict__, (item, self.__dict__)
        return self.__dict__[item]
