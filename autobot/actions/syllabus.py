import yaml

from tqdm import tqdm

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from autobot.concepts import Group, Coordinator, Meeting
from autobot.apis import ucf

from . import paths

"""Expected `syllabus.yml` format. You can also find this in `templates/seed/group/syllabus.yml`.

```yaml
- required:
    title: ""
    cover: ""
    filename: ""
    instructors: []
    description: >-

  optional:
    date: ""
    room: ""
    tags: []
    papers: []
    urls:
      slides: ""
      youtube: ""
    kaggle:
      datasets: []
      competitions: []
      kernels: []
      gpu: false
```
"""


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
    # TODO support undecided filenames
    for meeting, schedule in tqdm(
        zip(syllabus_yml, meeting_schedule), desc="Parsing Meetings"
    ):
        try:
            syllabus.append(Meeting(group, meeting, schedule))
        except AssertionError:
            tqdm.write(
                f"You're missing `required` fields from the meeting happening on {schedule.date} in {schedule.room}"
            )
            continue
    # endregion

    return syllabus


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
