from autobot.meta import Group


def update_notebooks(group: Group, auto_overwrite: bool = False) -> None:
    """Assumes the existence of the `syllabus.yml`.

    1. Updates Notebook metadata (e.g. instructors, dates, etc.)
    2. Updates the banner for the meeting / social media.
    """
    safety.force_root()
