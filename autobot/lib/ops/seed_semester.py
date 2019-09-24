import shutil
from pathlib import Path

from jinja2 import Template

from autobot import ORG_NAME
from autobot.meta import Group, Meeting
from autobot.lib import safety, log
from autobot.lib.configs import website


# go to the `autobot` root pkg dir
src_dir = Path(__file__).parent.parent.parent


def seed_semester(group: Group, auto_overwrite: bool = False) -> None:
    """Sets up the skeleton for a new semester.
    1. Copies base `yml` into `<group>/<semester>/`
    2. Sets up the Website's entires for the given semester. (NB: Does **not**
       make posts.)
    3. Performs a similar setup with Google Drive & Google Forms.
    4. Generates skeleton for the login/management system.
    """
    safety.force_root()

    # Safety check
    if auto_overwrite:
        overwrite = log.warning(f"About to delete {group.as_dir()}. ", prompt=True)
        if overwrite:
            shutil.rmtree(group.as_dir())

    if group.as_dir().exists():
        log.warning(f"{group.as_dir()} exists! Tread carefully.")
        raise FileExistsError("Found {group.as_dir()}; exiting.")

    # region 1. Copy base `yml` files.
    #   1. env.yml
    #   2. overhead.yml
    #   3. syllabus.yml
    # noinspection PyTypeChecker
    shutil.copytree(src_dir / "templates/seed/group", group.as_dir())

    # noinspection PyTypeChecker
    with open(group.as_dir() / "env.yml", "r") as f:
        env = Template(f.read())

    with open(group.as_dir() / "env.yml", "w") as f:
        f.write(env.render(org_name=ORG_NAME, group=group))
    # endregion

    # region 2. Setup Website for this semester
    assert website.CONTENT_DIR.exists()
    (website.CONTENT_DIR / group.as_dir()).mkdir(exist_ok=auto_overwrite)
    # endregion

    # region 3. Setup Google Drive & Google Forms setup
    # TODO: make Google Drive folder for this semester
    # TODO: make "Sign-Up" Google Form and Google Sheet
    # TODO: make "Sign-In" Google Form and Google Sheet
    # endregion
