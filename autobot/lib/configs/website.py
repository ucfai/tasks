from pathlib import Path

from autobot import ORG_NAME


page_url = f"{ORG_NAME}.org"
page_git = f"site"
site_dir = f"{ORG_NAME}.org"
repo_url = f"{ORG_NAME}/{page_git}"

# CONTENT_DIR = Path(f"{site_dir}/content")
CONTENT_DIR = Path(f"{site_dir}")
