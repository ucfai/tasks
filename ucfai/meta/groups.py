from ucfai.meta import SemesterMeta
from ucfai.meta.group import Group


class DataScience(Group):
    def __init__(self, sem_meta: SemesterMeta):
        super().__init__(name="Data Science", sem_meta=sem_meta)


class Intelligence(Group):
    def __init__(self, sem_meta: SemesterMeta):
        super().__init__(name="Intelligence", sem_meta=sem_meta)


class Competitions(Group):
    def __init__(self, sem_meta: SemesterMeta):
        super().__init__(name="Competitions", sem_meta=sem_meta)
