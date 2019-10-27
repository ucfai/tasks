def seed_semester(group: Group, forced_overwrite: bool = False):
    """Performs the initial semester setup.
    1. Copies base YAML from templates/seed/semester into `<group>/<semester>`
    2. Sets up website entries for the semester (doesn't make posts)
    """
    if forced_overwrite:
        overwrite = log.warning(f"About to delete {group.as_dir()}.", prompt=True)
        if overwrite:
            shutil.rmtree(RepoUtils.get_path(group))
            shutil.rmtree(SiteUtils.get_path(group))

    if group.as_dir().exists():
        log.warning(f"{group.as_dir()} exists! Tread carefully.")
        raise FileExistsError("Found {group.as_dir()}; exiting.")

    shutil.copytree(src / "templates/seed/group", RepoUtils.get_path(group))

    env = Template(open(RepoUtils.get_path(group) / "env.yml", "r").read())

    with open(RepoUtils.get_path(group) / "env.yml", "w") as f:
        f.write(env.render(org_name=ORG_NAME, group=group))

    # region 2. Setup Website for the semester
    SiteUtils.add_semester(group)
    # endregion

def init_semester(group: Group, forced_overwrite: bool = False):
    """Assumes a [partially] complete Syllabus; this will only create new
    syllabus entries' resources - thus avoiding potentially irreversible
    changes/delections.

    1. Reads `overhead.yml` to parse Coordinators and Meeting times.
    2. Reads `syllabus.yml` to parse the Syllabus and sets up Notebooks,
       Banners, and initial Website entries.
    """
    # region 1. Read `overhead.yml`
    overhead = yaml.load(open(RepoUtils.path(group) / "overhead.yml", "r"))
    coordinators = overhead["coordinators"]

    setattr(group, "coordinators", Coordinator.parse_yaml(coordinators))

    meetings = overhead["meetings"]
    offset = meetings["start_offset"]
    schedule = UCF.make_schedule(group, meetings, offset)
    # endregion

    # region 2. Read `syllabus.yml`
    syllabus = yaml.load(open(RepoUtils.path(group) / "syllabus.yml", "r"))

    meetings = []
    for meeting, location in zip(syllabus, schedule):
        try:
            meetings.append(Meeting(group, meeting, location))
        except AssertionError:
            print("You're missing `required` fields from the meeting happening "
                  f"on {schedule.date} in {schedule.room}!")
            continue

    for meeting in meetings:
        NBUtils.touch(meeting, overwrite=forced_overwrite)
        SiteUtils.touch(meeting, overwrite=forced_overwrite)
        SiteUtils.banner(meeting, overwrite=forced_overwrite)
    # endregion
    pass
