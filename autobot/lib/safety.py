from pathlib import Path
import os

from autobot.meta import Group, Meeting


def force_root():
    # safety.py \ lib \ autobot \ <autobot-root> \ <jenkins-root>
    path = Path(__file__).parent.parent.parent.parent

    os.chdir(path)


def can_overwrite(meeting: Meeting, overwrite: bool = False):
    if overwrite:
        return True

    if meeting.repo_path.exists():
        # check that the repository entry doesn't exist
        overwrite = input(f"`{meeting.repo_path}` exists. Overwrite? [y/N] ")
        return overwrite.lower() in ["y", "yes"]
    elif meeting.site_path.exists():
        # check that the website entry doesn't exist
        overwrite = input(f"`{meeting.site_path}` exists. Overwrite? [y/N] ")
        return overwrite.lower() in ["y", "yes"]
    else:
        # check that we haven't updated the names of things
        pass
