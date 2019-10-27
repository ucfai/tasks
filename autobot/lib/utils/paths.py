from pathlib import Path

from autobot import ORG_NAME
from autobot.meta import Group, Meeting

# region Repository pathing utilities
def repo_group_folder(group: Group):
    """Produces the Group's directory, with respect to the current semester."""
    return Path(repr(group)) / group.semester.short


def repo_meeting_folder(meeting: Meeting, short: bool = False, fully_qualified_path: bool = False):
    """Generates the Meeting's directory, with optional parameters for the
    fully qualified path, which would be something similar to:
    `<group>/<semester>/<filename>`, e.g. consider the Fall 2019 Computational
    Cognitive Neuroscience meeting: `core/fa19/2019-11-20-ccn`."""
    if short:
        return Path(repr(meeting))
    return repo_group_folder(meeting.group) / repo_meeting_folder(meeting, short=True)

# endregion

# region Website pathing utilities
page_url = f"{ORG_NAME}.org"
page_git = f"{ORG_NAME}.org"
site_dir = f"{ORG_NAME}.org"
repo_url = f"{ORG_NAME}/{page_git}"

CONTENT_DIR = Path(site_dir)

def site_post(meeting):
    """Utility function to calculate necessary paths for the website."""
    # TODO: Migrate to Hugo

    # currently written for Jekyll
    return CONTENT_DIR / repr(meeting.group) / "_posts" / repr(meeting)


def site_post_assets(meeting):
    """Calculate the path for assets related to a given "meeting." This function
    is specified to provide a descriptive interface for what are considered
    assets to a given post vs the post itself.
    """
    return site_post(meeting)


def site_data(meeting):
    pass

def site_group_folder(group):
    path = CONTENT_DIR / repr(group) / group.semester.short
    path.mkdir(exists_ok=True, parents=True)
    return path

# endregion
