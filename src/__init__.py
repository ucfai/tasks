import json
from pathlib import Path

from invoke import Collection
from jinja2 import Environment, PackageLoader
from ruamel.yaml import YAML


j2env = Environment(loader=PackageLoader("tasks", "src/templates"),)
j2env.filters["jsonify"] = json.dumps


from .concepts import Group, Meeting

yaml = YAML()
yaml.register_class(Meeting)
yaml.register_class(Group)
config = yaml.load(open(Path(__file__).parent.parent / "config.yml"))


def configure_context(ctx, group: str = "", semester: str = ""):
    # Prefer values set in Context over arguments
    if "group" in ctx:
        group = ctx["group"]
    if "semester" in ctx:
        semester = ctx["semester"]

    try:
        if not isinstance(group, Group):
            group = yaml.load(open(Path(group) / semester / "overhead.yml", "r"))
    except FileNotFoundError:
        if not semester:
            from .tools import ucfcal

            group = ucfcal.determine_semester(group)
        else:
            group = Group(name=group, semester=semester)
    finally:
        ctx["group"] = group

    try:
        syllabus = yaml.load(open(group.asdir() / "syllabus.yml", "r"))
    except FileNotFoundError:
        syllabus = []
    finally:
        ctx["syllabus"] = syllabus

    ctx["path"] = ctx["group"].asdir()


__all__ = []
from . import semester
# from . import solutionbook
# from . import papers
__all__ += [
    "semester",
    # "solutionbook",
    # "papers"
]
# from . import hugo
# from . import kaggle
# from . import sendgrid
# from . import youtube
__all__ += [
    # "hugo",
    # "kaggle",
    # "sendgrid",
    # "youtube",
]
