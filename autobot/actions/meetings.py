import json

import requests
from tqdm import tqdm

from autobot.actions import paths
from autobot.apis import kaggle
from autobot.apis.nbconvert import (
    SolutionbookToPostExporter,
    SolutionbookToWorkbookExporter,
    TemplateNotebookValidator,
    FileExtensions,
)
from autobot.concepts import Meeting
from autobot.pathing import templates, repositories


def update_or_create_folders_and_files(meeting: Meeting):
    """Performs some initial directory creation / cleanup. Currently this
    implementation is quite destructive. Ideally, there's some way to go about
    *intelligently* merging work ~ so this would allow for some temporary titles
    and the like.

    Present file locations:
      - <group>/<semester>/<repr(meeting)>/<repr(meeting)>.solution.ipynb
      - ucfai.org/content/<group>/<semester>/<meeting-filename>.md
    """
    # TODO rename `placeholder` notebooks
    #      this requires changes in both the `paths.repo_meeting_folder` as well as the
    #      `paths.site_post`
    # TODO implement a way to track meetings – since `hugo-academic`'s docs doesn't
    #      work the same way Jekyll posts did (YYYY-MM-DD-<filename>.md), we need a new
    #      way to uniquely identify meetings (so we know which to clean and such)
    #      NOTE we might just be able to totally overwrite the group's contents on the
    #           site, since everything in, say, `core/fa19/*` (minus `_index.md`) is
    #           generated from the meeting's Solutionbook
    # TODO allow for meetings to be moved – this intuitively makes sense to resolve
    #      with the `filename` parameter, but may also need to consider the `date` (you
    #      can get all this from `repr(meeting)`)
    path = repositories.local_meeting_root(meeting)

    root = repositories.local_semester_root(meeting)

    local_neighbors = list(root.iterdir())

    for d in local_neighbors:
        date, name = d.stem[:10], d.stem[11:]

        # remove placeholder
        # rename by date
        shares_meet = ("meeting" in name and int(name[-2:]) == meeting.number - 1)
        shares_date = (date == repr(meeting)[:10])
        if d.stem != repr(meeting) and (shares_meet or shares_date):
            old_path = d
            old_soln = d / "".join([d.stem, FileExtensions.Solutionbook])

            new_path = old_path.with_name(repr(meeting))
            new_soln = old_path / "".join([repr(meeting), FileExtensions.Solutionbook])

            # NOTE: rename internal files before renaming the folder
            tqdm.write(f"renaming: {old_soln} -> {new_soln}")
            old_soln.rename(new_soln)
            tqdm.write(f"renaming: {old_path} -> {new_path}")
            old_path.rename(new_path)
            return
        # TODO: handle meeting swaps (e.g. meeting02 with meeting 06, etc.)
        # TODO: handle meeting renames with swaps
        # TODO: allow for renaming to propagate through to platforms like Kaggle

    path.mkdir(exist_ok=True, parents=True)


""" Use the following as "inspiration", this feels like it's far too complex to understand
def update_or_create_folders_and_files(meeting: Meeting):
    Performs some initial directory creation / cleanup. Currently this
    implementation is quite destructive. Ideally, there's some way to go about
    *intelligently* merging work ~ so this would allow for some temporary titles
    and the like.
    repo_path = paths.repo_meeting_folder(meeting)
    site_path = paths.site_post(meeting)

    date = str(repo_path.stem)[:10]  # this is a wonky ISO date thing

    repo_neighbors = pd.Series(data=os.listdir(repo_path.parent))
    repo_matching = repo_neighbors.loc[repo_neighbors.str.startswith(date)]

    if len(repo_matching) == 0:
        repo_path.mkdir(exist_ok=True, parents=True)
    else:
        for match in repo_matching.values:
            if repo_path.exists() and match != repo_path.stem:
                # NOTE: this currently deletes all non-conforming directories
                #   it might be wise to merge them, but unsure how.
                shutil.rmtree(repo_path.with_name(match))
            elif match != repo_path.stem:
                # rename the folder
                repo_path.with_name(match).rename(repo_path)

                try:
                    # NOTE: honestly, Workbooks are derived from Solutionbooks, so maybe
                    #       we just ignore Workbooks and dump them?
                    old_workbook = match + FileExtensions.Workbook
                    new_workbook = repo_path.with_suffix(FileExtensions.Workbook)
                    (repo_path / old_workbook).rename(new_workbook)
                except FileNotFoundError:
                    pass

                try:
                    old_solution = match + FileExtensions.Solutionbook
                    new_solution = repo_path.with_suffix(FileExtensions.Solutionbook)
                    (repo_path / old_solution).rename(new_solution)
                except FileNotFoundError:
                    pass

    site_neighbors = pd.Series(data=os.listdir(site_path.parent))
    site_matching = site_neighbors.loc[site_neighbors.str.startswith(date)]

    if len(site_matching) == 0:
        site_path.mkdir(exist_ok=True)
    else:
        for match in site_matching.values:
            if site_path.exists() and match != site_path.stem:
                # this should be destructive as the repo informs the site.
                shutil.rmtree(site_path.with_name(match))
            elif match != site_path.stem:
                # rename the folder
                site_path.with_name(match).rename(site_path)

                try:
                    old_post = match + ".md"
                    new_post = site_path.with_suffix(".md")
                    (site_path / old_post).rename(new_post)
                except FileNotFoundError:
                    pass
"""


def update_or_create_notebook(meeting: Meeting, overwrite: bool = False):
    """Notebooks are the nuts and bolts of AI@UCF. These power the website's
    posts, our workshops, and are the general workbooks students can make use
    of.

    This function generates notebooks for a given meeting. *If the notebook
    exists*, a prompt will be issued for destructive actions. Otherwise, the
    notebook is strictly injected with the appropriate metadata and headings
    without losing content in the notebook.
    """
    # Validates this meeting's notebook conforms to expectations details in:
    #   https://ucfai.org/docs/admin/making-meetings/
    validator = TemplateNotebookValidator()
    _, _ = validator.from_meeting(meeting)

    kernel_metadata = templates.load("meeting/kernel-metadata.json.j2")

    meeting.optional["kaggle"]["competitions"].insert(
        0, kaggle.slug_competition(meeting)
    )

    # TODO get this sorted into proper JSON and templating
    text = (
        kernel_metadata.render(
            slug=kaggle.slug_kernel(meeting),
            notebook=repr(meeting),
            kaggle=meeting.optional["kaggle"],
        )
        .replace("'", '"')  # JSON doesn't like single-quoted strings
        .lower()
    )

    open(paths.repo_meeting_folder(meeting) / "kernel-metadata.json", "w").write(text)

    # Converts a "Solutionbook" (`.solution.ipynb`) to a "Workbook" (`.ipynb`).
    #   Makes use of Preprocessors and FileWriters to place generate and write the
    #   notebook.
    workbook = SolutionbookToWorkbookExporter()
    _, _ = workbook.from_meeting(meeting)


def download_papers(meeting: Meeting):
    if not meeting.optional["papers"]:
        return

    folder = paths.repo_meeting_folder(meeting)

    for title, link in meeting.optional["papers"].items():
        with open(folder / f"{title}.pdf", "wb") as pdf:
            pdf.write(requests.get(link).content)


def export_notebook_as_post(meeting: Meeting):
    """Every notebook should also have a home on the website. This runs said
    notebook through the exporter so that it can be posted on the website.

    NOTE: This function is destructive. It will overwrite the post it's
    exporting to - this is intentional behavior, ergo **do not edit posts
    directly**.

    TODO: generalize to a utility function which is independent of a meeting,
    so that notebooks can generally be posted, since we don't have time for all
    the topics...
    """
    as_post = SolutionbookToPostExporter()
    post, resources = as_post.from_meeting(meeting)
