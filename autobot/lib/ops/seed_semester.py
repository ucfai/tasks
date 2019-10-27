import shutil
from pathlib import Path

from jinja2 import Template

from autobot import ORG_NAME
from autobot.meta import Group, Meeting
from autobot.lib import safety, log
from autobot.lib.configs import website


def seed_semester(group: Group) -> None:
    """Sets up the skeleton for a new semester.
    1. Copies base `yml` into `<group>/<semester>/`
    2. Sets up the Website's entires for the given semester. (NB: Does **not**
       make posts.)
    3. Performs a similar setup with Google Drive & Google Forms.
    4. Generates skeleton for the login/management system.
    """
    if paths.repo_group_folder(group).exists():
        log.warning(f"{paths.repo_group_folder(group)} exists! Tread carefully.")
        overwrite = input("The following actions **are destructive**. "
                          "Continue? [y/N] ")
        if overwrite.lower() not in ["y", "yes"]:
            return
    
    # region 1. Copy base `yml` files.
    #   1. env.yml
    #   2. overhead.yml
    #   3. syllabus.yml
    # strong preference to use `shutil`, but can't use with existing dirs
    # shutil.copytree("autobot/templates/seed/meeting", path.parent)
    copy_tree("autobot/templates/seed/group", str(paths.repo_group_folder(group)))

    env_yml = paths.repo_group_folder(group) / "env.yml"
    env = Template(open(env_yml, "r").read())

    with open(env_yml, "w") as f:
        f.write(env.render(org_name=ORG_NAME, group=group))
    # endregion

    # region 2. Setup Website for this semester
    paths.site_group_folder(group)
    # endregion

    # region 3. Setup Google Drive & Google Forms setup
    # TODO: make Google Drive folder for this semester
    # TODO: make "Sign-Up" Google Form and Google Sheet
    # TODO: make "Sign-In" Google Form and Google Sheet
    # endregion
