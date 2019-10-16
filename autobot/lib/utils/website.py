from pathlib import Path

from autobot import ORG_NAME

# from autobot.meta import Meeting

page_url = f"{ORG_NAME}.org"
page_git = f"site"
site_dir = f"{ORG_NAME}.org"
repo_url = f"{ORG_NAME}/{page_git}"

# CONTENT_DIR = Path(f"{site_dir}/content")
CONTENT_DIR = Path(site_dir)

# def post_path(meeting: Meeting):
def post_path(meeting):
    """Utility function to calculate necessary paths for the website."""
    # TODO: Migrate to Hugo

    # currently written for Jekyll
    return CONTENT_DIR / repr(meeting.group) / "_posts" / repr(meeting)


# def data_path(meeting: Meeting):
def data_path(meeting):
    pass
