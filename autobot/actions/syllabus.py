import yaml
from tqdm import tqdm

from autobot.apis import ucf
from autobot.pathing import templates, repositories
from autobot.concepts import Coordinator, Group, Meeting

from . import paths

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import copy


# TODO migrate from PyYAML to Confuse: https://github.com/beetbox/confuse


def init(group: Group):
    path = repositories.local_semester_root(group)

    assert not (path / "syllabus.yml").exists(), "found: syllabus.yml"
    assert (path / "overhead.yml").exists(), "found: overhead.yml"

    syllabus = yaml.load(open(templates.get("group/syllabus.yml"), "r"), Loader=Loader)
    overhead = yaml.load(open(path / "overhead.yml", "r"), Loader=Loader)["meetings"]

    # assert (
    #     overhead["start_offset"] >= 0
    # ), "Need to know the week we start this group to do anything else..."

    try:
        schedule = ucf.make_schedule(group, overhead)
    except AssertionError:
        # don't require `overhead` to be properly filled out
        schedule = [None] * (
            ucf.SEMESTER_LEN[group.semester.name.lower()] - overhead["start_offset"]
        )
    finally:
        meetings = {}
        for idx, meeting in tqdm(enumerate(schedule), desc="Initial Meeting Setup"):
            # TODO add support for non-standard meeting times
            if hasattr(meeting, "date"):
                syllabus["optional"]["date"] = meeting.date.isoformat()

            if hasattr(meeting, "room"):
                syllabus["optional"]["room"] = meeting.room

            meetings[f"meeting{idx:02d}"] = copy.deepcopy(syllabus)

        yaml.dump(
            meetings,
            stream=open(path / "syllabus.yml", "w"),
            Dumper=Dumper,
            width=80,
            sort_keys=False,
            # default_style='"',
        )


def sort(group: Group):
    path = repositories.local_semester_root(group)

    assert (path / "syllabus.yml").exists()
    assert (path / "overhead.yml").exists()

    overhead = yaml.load(open(path / "overhead.yml", "r"), Loader=Loader)["meetings"]
    schedule = ucf.make_schedule(group, overhead)

    syllabus_old = yaml.load(open(path / "syllabus.yml", "r"), Loader=Loader)
    syllabus_new = {}

    # resort entries
    for idx, previous in tqdm(
        enumerate(syllabus_old.values()), desc="Resorting Syllabus"
    ):
        syllabus_new[f"meeting{idx:02d}"] = copy.deepcopy(previous)

    # re-date the entries
    for meeting, info in tqdm(zip(syllabus_new.keys(), schedule), desc="Update Dates"):
        syllabus_new[meeting]["optional"]["date"] = info.date.isoformat()

    yaml.dump(
        syllabus_new,
        stream=open(path / "syllabus.yml", "w"),
        Dumper=Dumper,
        width=80,
        sort_keys=False,
        # default_style='"',
    )


def parse(group: Group):
    path = repositories.local_semester_root(group)

    # region 1. Read `overhead.yml` and seed Coordinators
    overhead = yaml.load(open(path / "overhead.yml", "r"), Loader=Loader)
    setattr(group, "coords", Coordinator.parse_yaml(overhead))

    # TODO validate dates follow the meeting pattern and ping Discord if not
    overhead = overhead["meetings"]
    schedule = ucf.make_schedule(group, overhead)
    # endregion

    # region 2. Read `syllabus.yml` and parse Syllabus
    syllabus = yaml.load(open(path / "syllabus.yml", "r"), Loader=Loader)

    meetings = []
    # TODO support undecided filenames
    for (key, meeting), when_where in tqdm(
        zip(syllabus.items(), schedule), desc="Parsing Meetings"
    ):
        # implicitly trust `syllabus.yml` to be correct
        if not meeting["optional"].get("room", False):
            meeting["optional"]["room"] = when_where.room

        if not meeting["optional"].get("date", False):
            meeting["optional"]["date"] = when_when.date.isoformat()

        meetings.append(Meeting(group, meeting, tmpname=key))
        # try:
        #     meetings.append(Meeting(group, meeting, key))
        # except AssertionError:
        #     tqdm.write(
        #         f"You're missing `required` fields from the meeting happening on {meeting.date} in {schedule.room}"
        #     )
        #     continue
    # endregion

    return meetings


def write(group: Group):
    # TODO write things like meeting dates and rooms (iff not in syllabus.yml) to avoid imputing - since this can be less than ideal for some actions
    # TODO write template meetings to syllabus
    #      each group has 10-11 meetings, so we might be able to just output each of
    #      them and make it a little more obvious what meeting count and date we're on?
    raise NotImplementedError()


def format(group: Group):
    # TODO anything beyond 88 chars should be wrapped, trying to wrap on the nearest word
    # TODO extract things like the ID from a URL (e.g. YouTube's) and write that back to the syllabus
    raise NotImplementedError()


def healthcheck(group: Group):
    # TODO validate meeting dates match the weekdate – iff `strict_dates` (or something like that)
    # TODO validate that meeting names don't clash
    # TODO fire off a discord notification if a healthcheck fails
    # TODO validate the url are either match the full-on URL or the identifier the platform uses
    #      e.g. youtube uses: https://youtube.com/watch?v=<some-id>, so either pass that or if someone puts <some-id> accept that
    raise NotImplementedError()
