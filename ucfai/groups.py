from pathlib import Path

from .groups_utils import SemesterMeta


class Group:
    def __init__(self, name: str, sem_meta: SemesterMeta) -> None:
        self.name = name
        self.sem = sem_meta
        self.coords = None
        self.prim_mtgs = None
        self.supp_mtgs = None

    def __str__(self) -> str:
        return f"{self.name} Group, {self.sem}"

    def __repr__(self) -> str:
        return self.name.lower().replace(" ", "-")

    def _to_dir(self):
        return Path(repr(self)) / self.sem.short

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def schedule(self):
        pass
        # raise NotImplementedError()


class DataScience(Group):
    def __init__(self, sem_meta: SemesterMeta):
        super().__init__(name="Data Science", sem_meta=sem_meta)


class Intelligence(Group):
    def __init__(self, sem_meta: SemesterMeta):
        super().__init__(name="Intelligence", sem_meta=sem_meta)


class Competitions(Group):
    def __init__(self, sem_meta: SemesterMeta):
        super().__init__(name="Competitions", sem_meta=sem_meta)
