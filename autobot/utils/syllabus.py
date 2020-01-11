import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from autobot.meta import Group
from autobot.apis import ucf

from . import paths

def parse(group: Group):
    # region 1. Read `overhead.yml` and seed Coordinators
    overhead_yml = paths.repo_group_folder(group) / "overhead.yml"
    overhead_yml = yaml.load(open(overhead_yml, "r"), Loader=Loader)
    coordinators = overhead_yml["coordinators"]
    setattr(group, "coords", Coordinator.parse_yaml(coordinators))

    meeting_overhead = overhead_yml["meetings"]
    meeting_schedule = ucf.make_schedule(group, meeting_overhead)
    # endregion

    # region 2. Read `syllabus.yml` and parse Syllabus
    syllabus_yml = paths.repo_group_folder(group) / "syllabus.yml"
    syllabus_yml = yaml.load(open(syllabus_yml, "r"), Loader=Loader)

    syllabus = []
    for meeting, schedule in tqdm(zip(syllabus_yml, meeting_schedule), desc="Parsing Meetings"):
        try:
            syllabus.append(Meeting(group, meeting, schedule))
        except AssertionError:
            tqdm.write(f"You're missing `required` fields from the meeting happening on {schedule.date} in {schedule.room}")
            continue
    # endregion

    return syllabus

def write(group: Group):
    # TODO (@ch1pless) write things like meeting dates and rooms (iff not in syllabus.yml) to avoid imputing - since this can be less than ideal for some actions
    raise NotImplementedError()

def format(group: Group):
    # TODO (@ch1pless) word-wrap the syllabus to 88 characters (where possible) to make for easier reading
    raise NotImplementedError()