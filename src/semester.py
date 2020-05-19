import copy
import os
import re
from hashlib import sha256
from pathlib import Path
from typing import Tuple

import numpy as np
from invoke import task

from . import configure_context, yaml, j2env
from .concepts import Meeting
from .tools import apply, status, ucfcal


def _format_and_comment_syllabus_yml(ctx, write):
    syllabus_path = ctx["path"] / "syllabus.yml"
    yaml.dump(write, open(syllabus_path, "w"))

    text = open(syllabus_path, "r").read()

    text = re.sub(r"- !Meeting", r"\n\g<0>", text)
    text = re.sub(
        r"\n  optional:.*", r"\n\g<0>  # all keys are listed in the docs", text
    )

    text = re.sub(r"abstract: \>", r"\g<0>-", text)
    text = re.sub(r"(?P<abstract>abstract: \>-)*", r"\g<abstract>", text)

    open(syllabus_path, "w").write(text)


@task
def load(ctx):
    """Reads Group/Syllabus and adds them to Context for use with other functions.
    """
    configure_context(ctx)
    # region 1. Read `overhead.yml` and seed Coordinators
    # TODO validate dates follow the meeting pattern and ping Discord if not
    ctx["group"] = ctx["group"].flatten()
    group = ctx["group"]

    status.test(group.startdate, "Group needs `startdate` to proceed with generation.")
    # endregion

    # region 2. Read `syllabus.yml` and parse Syllabus
    syllabus = ctx["syllabus"]
    meetings = []

    def _parse_yml(meeting):
        # implicitly trust `syllabus.yml` to be correct
        if not meeting.required["room"]:
            meeting.required["room"] = group.room

        missing = set(meeting.authors).intersection(group.authors)
        if len(missing) > 0:
            status.warn(f"Could not find authors: {missing}. Please add them.")

        meetings.append(meeting)

    apply(_parse_yml, syllabus)
    status.success("Successfully read `syllabus.yml`.")
    # endregion

    ctx["syllabus"] = [x.flatten() for x in meetings]


@task(pre=[load])
def touch(ctx):
    syllabus = {m.id: ctx["path"] / str(m) for m in ctx["syllabus"]}

    ondisk = sorted([x for x in ctx["path"].glob("??-??-*/") if x.is_dir()])
    ondisk = {open(p / ".metadata", "r").read(): p for p in ondisk}

    # region Create/rename folders
    created = 0
    for sha, meeting in syllabus.items():
        if sha in ondisk:  # meeting exists on disk
            ondisk[sha].rename(meeting)
        else:  # meeting does not exist on disk
            meeting.mkdir()
            with open(meeting / ".metadata", "w") as f:
                f.write(sha)
            created += 1

    if created / len(syllabus) > 0.5:
        status.success("Created syllabus's meeting directories.")
    else:
        status.success("Updated syllabus's meeting directories.")
    # endregion

    # region Rename matching folder contents
    for sha, meeting in syllabus.items():
        prv_name = ondisk[sha].stem[6:]  # only look at filenames
        new_name = meeting.stem[6:]  # only look at filenames

        for child in meeting.iterdir():
            if child.stem.startswith(prv_name):
                ext = "".join(child.suffixes)
                child.rename(child.parent / f"{new_name}{ext}")
    # endregion


@task(post=[touch])
def seed(ctx, group, semester=""):
    """Creates `group.yml` for the semester. Must be filled before calling `create`.
    """
    configure_context(ctx, group, semester)
    group = ctx["group"]

    try:
        ctx["path"].mkdir()
    except FileExistsError:
        status.fail(f"Found {ctx['path']}. Existing...")
        exit(0)

    inv = j2env.get_template("group/invoke.yml.j2")
    inv = inv.render(group=group.name, semester=group.semester)
    inv = yaml.load(inv)

    schedule = ucfcal.temp_schedule(group.semester)
    group.startdate = str(schedule[0])

    files_to_write = {
        # Write Group metadata to file
        ctx["path"] / "overhead.yml": group,
        # Write Context to file (e.g. group-name and semester)
        ctx["path"] / "invoke.yml": inv,
        ctx["path"].parent / "invoke.yml": inv,
    }

    for filepath, contents in files_to_write.items():
        yaml.dump(contents, open(filepath, "w"))
        status.success(f"Wrote {filepath}.")

    meetings = []

    def _add_meetings(meeting):
        idx, date = meeting
        date = date.isoformat() if date else ""
        placeholder = f"meeting{idx:02d}"
        meeting_id = sha256(placeholder.encode("utf-8")).hexdigest()
        meetings.append(
            Meeting(
                required={
                    "id": meeting_id,
                    "title": placeholder,
                    "date": date,
                    "filename": placeholder,
                }
            )
        )

    apply(_add_meetings, list(enumerate(schedule)))
    _format_and_comment_syllabus_yml(ctx, write=meetings)
    status.success(f"Created `{ctx['path'] / 'syllabus.yml'}`.")


@task(pre=[load])
def sort(ctx):
    """Sorts Meetings based on their Date.
    """
    schedule = ucfcal.make_schedule(ctx["group"])

    syllabus_base = ctx["syllabus"]
    base_idx = np.arange(len(syllabus_base) + 1)
    sort_idx = sorted(syllabus_base, key=lambda x: x.required["date"])
    sort_idx = [syllabus_base.index(x) for x in sort_idx]
    syllabus_sort = [None] * len(sort_idx)

    n_uniq = len({x.required["date"] for x in syllabus_base})
    n_base = len(syllabus_base)
    status.test(
        (n_uniq == n_base),
        "Collision found. Meetings must have unique dates. Recheck `syllabus.yml`.",
    )

    # resort entries
    def _resort(t: Tuple):
        base, sort, date = t
        base_required = copy.copy(syllabus_base[sort].required)
        base_required["date"] = date
        base_optional = copy.copy(syllabus_base[sort].optional)
        syllabus_sort[base] = Meeting(base_required, base_optional)

    apply(_resort, list(zip(base_idx, sort_idx, schedule)))

    _format_and_comment_syllabus_yml(ctx, write=syllabus_sort)

    ctx["syllabus"] = [x.flatten() for x in syllabus_sort]

    status.success("Successfully reordered `syllabus.yml`.")
