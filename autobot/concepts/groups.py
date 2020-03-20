"""NB: Update the `ACCCEPTED` constant at the base of this file when adding a
new group!"""
from autobot.concepts import Semester

from .group import Group


class Core(Group):
    def __init__(self, sem_meta: Semester):
        super().__init__(name="Core", sem_meta=sem_meta)


class Intelligence(Group):
    def __init__(self, sem_meta: Semester):
        super().__init__(name="Intelligence", sem_meta=sem_meta)


class DataScience(Group):
    def __init__(self, sem_meta: Semester):
        super().__init__(name="Data Science", sem_meta=sem_meta)


class Competitions(Group):
    def __init__(self, sem_meta: Semester):
        super().__init__(name="Competitions", sem_meta=sem_meta)


class Supplementary(Group):
    def __init__(self, sem_meta: Semester):
        super().__init__(name="Supplementary", sem_meta=sem_meta)


ACCEPTED = {
    "core": Core,
    "intelligence": Intelligence,
    "data-science": DataScience,
    "competitions": Competitions,
    "supplementary": Supplementary,
}
