# import logging
# from datetime import datetime as dt
#
# import nbconvert as nbc
#
# from fabric import task
#
# from meta import SemesterMeta, ACCEPTED_GRP
# from meta.coordinator import Coordinator
# from tooling.aux import *
#
# log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)
#
# # region Public Methods ########################################################
# # These should begin with a character.
# __all__ = ["seed_semester", "prepare_ntbks", "convert_ntbks"]
#
#
# def _generate_group(group: str):
#     assert group in ACCEPTED_GRP.keys()
#     sem = which_semester()
#     grp = ACCEPTED_GRP[group](sem)
#     return grp
#
# # TODO: Add Type-hints to @tasks once supported
#
#
# @task
# def seed_semester(group):
#     """Performs initial semester setup.
#     1. Copies base YAML into `<grp>/<sem>/`
#     2. Sets up the Website entries for the semester (doesn't make posts)
#     3. Performs setup with Google Drive & Forms
#
#     :param group: str
#     """
#     assert type(group) is str
#     grp = _generate_group(group)
#     chk_root(grp)
#     # Safety check.
#     if grp.as_dir().exists():
#         log.warning(f"I see that {grp.as_dir()} exists! Tread carefully.")
#         raise ValueError(f"Found {grp.as_dir()}; exiting.")
#
#     # region 1. Copy base YAML files {env, overhead, syllabus}.yml
#     import shutil
#     parent: Path = Path(__file__).parent
#     # noinspection PyTypeChecker
#     shutil.copytree(parent / "seed", grp.as_dir())
#
#     # noinspection PyTypeChecker
#     with open(grp.as_dir() / "env.yml", "r") as f:
#         env = Template(f.read())
#
#     # noinspection PyTypeChecker
#     with open(grp.as_dir() / "env.yml", "w") as f:
#         f.write(env.render(sem_meta=grp.sem))
#     # endregion
#
#     # region 2. Setup Website for this semester
#     assert SITE_CONTENT_DIR.exists()
#     (SITE_CONTENT_DIR / grp.as_dir()).mkdir()
#     # endregion
#
#     # region 3. Operate on Google Drive & Google Forms
#     # TODO: make Google Drive folder for this semester
#
#     # TODO: make "Sign Up" Google Form and Google Sheet
#
#     # TODO: make "Sign Out" Google Form and Google Sheet
#     # endregion
#
#
# @task
# def prepare_ntbks(group):
#     """Assumes a complete (or partially complete) Syllabus; this will only
#     create new Syllabus entries and won't make other changes (to avoid
#     irreversible deletions).
#     """
#     assert type(group) is str
#     grp = _generate_group(group)
#     chk_root(grp)
#
#     # region Read `overhead.yml` and seed Coordinators
#     # noinspection PyTypeChecker
#     overhead = yaml.load(open(grp.as_dir() / "overhead.yml"))
#     overhead_coordinators = overhead["coordinators"]
#     setattr(grp, "coords", Coordinator.parse_yaml(overhead_coordinators))
#     # endregion
#
#     # region Read `syllabus.yml` and setup Notebooks
#     # noinspection PyTypeChecker
#     syllabus = yaml.load(open(grp.as_dir() / "syllabus.yml"))
#     overhead_meetings = overhead["meetings"]
#
#     def _parse_and_make_meetings(key: str) -> None:
#         abbr = {"prim": "primary", "supp": "supplementary"}
#         mtg_meta = make_schedule(grp, overhead_meetings[abbr[key]])
#         meetings = [Meeting(**Meeting.parse_yaml(mtg, grp.coords, meta))
#                     for mtg, meta in zip(syllabus[abbr[key]], mtg_meta)]
#         setattr(grp, f"{key}_sched", mtg_meta)
#
#         for mtg in meetings:
#             make_notebook(grp, mtg)
#             prepares_post(grp, mtg)
#
#     # region `Primary` meetings
#     _parse_and_make_meetings("prim")
#     # endregion
#     # region `Supplementary` meetings
#     if "supplementary" in syllabus.keys():
#         _parse_and_make_meetings("supp")
#     # endregion
#
#     # endregion
#
#
# @task
# def convert_ntbks(group):
#     assert type(group) is str
#     grp = _generate_group(group)
#     chk_root(grp)
#
#     export = nbc.LatexExporter()
#     export.template_path = res_dir / "templates" / "notebooks"
#     export.template_file = "nb-as-post"
#
#     # TODO: notebook conversion to Post w/ Front-Matter
#
#
# def which_semester() -> SemesterMeta:
#     """A static method which determines the current semester based on the
#     present date and uses the UCF calendar redirect to inform its decision.
#
#     :return: SemesterMeta
#     """
#     cal_url = requests.get(UCF_CAL_URL).url
#     curr_dt = dt.now()
#
#     may, aug, dec = [5, 8, 12]  # May, Aug, Dec (1-based)
#
#     if curr_dt.month in [may, aug, dec]:
#         if cal_url.endswith("fall") and curr_dt.month == dec:
#             cal_url = cal_url.replace("fall", "spring").replace(
#                 f"{curr_dt.year}", f"{curr_dt.year + 1}"
#             )
#         elif cal_url.endswith("summer") and curr_dt.month == aug:
#             cal_url = cal_url.replace("summer", "fall")
#         elif cal_url.endswith("spring") and curr_dt.month == may:
#             cal_url = cal_url.replace("spring", "summer")
#
#     year, name = cal_url.replace(f"{UCF_CAL_URL}/", "").split("/")
#     short = name[:2] + year[2:]
#
#     return SemesterMeta(name, year, short)
