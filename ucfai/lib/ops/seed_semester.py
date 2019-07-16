def seed_semester(grp: Group, auto_overwrite: bool = False) -> None:
    """Sets up the skeleton for a new semester.
    1. Copies base `yml` into `<group>/<semester>/`
    2. Sets up the Website's entires for the given semester. (NB: Does **not**
       make posts.)
    3. Performs a similar setup with Google Drive & Google Forms.
    4. Generates skeleton for the login/management system.
    """
    safety.chk_root(grp)

    # Safety check
    if grp.as_dir().exits():
        log.warning(f"{grp.as_dir()} exists! Tread carefully.")
        raise FileExistsError("Found {grp.as_dir()}; exiting.")

    # region 1. Copy base `yml` files.
    #   1. env.yml
    #   2. overhead.yml
    #   3. syllabus.yml
    import shutil
    # noinspection PyTypeChecker
    shutil.copytree(res_dir / "templates/seed", grp.as_dir())

    # noinspection PyTypeChecker
    with open(grp.as_dir() / "env.yml", "r") as f:
        env = Template(f.read())

    with open(grp.as_dir() / "env.yml", "w") as f:
        f.write(env.render(sem_meta=grp.sem))
    # endregion

    # region 2. Setup Website for this semester
    assert SITE_CONTENT_DIR.exists()
    (SITE_CONTENT_DIR / grp.as_dir()).mkdir()
    # endregion

    # region 3. Setup Google Drive & Google Forms setup
    # TODO: make Google Drive folder for this semester
    # TODO: make "Sign-Up" Google Form and Google Sheet
    # TODO: make "Sign-In" Google Form and Google Sheet
    # endregion
