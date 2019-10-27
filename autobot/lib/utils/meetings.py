import io
import os
import copy
import datetime
import shutil
import subprocess
import warnings
from pathlib import Path
from hashlib import sha256
from typing import List, Dict
from itertools import product
from distutils.dir_util import copy_tree

import imgkit
import requests
import yaml
from PIL import Image
import pandas as pd
import numpy as np
from jinja2 import Template
import nbformat as nbf
import nbconvert as nbc
from nbgrader.preprocessors import ClearSolutions, ClearOutput

from autobot import get_template
from autobot.meta.meeting import Meeting
from autobot.lib.utils import paths
from autobot.lib.apis import kaggle


class Suffixes:
    SOLUTION = ".solution.ipynb"
    WORKBOOK = ".ipynb"


class Solution:
    BEGIN = "### BEGIN SOLUTION"
    END   = "### END SOLUTION"


def read(meeting: Meeting, suffix: str = Suffixes.WORKBOOK):
    """Attempts to read a Notebook for a given Meeting. If it can't find the
    notebook it will touch the notebook gracefully and move on."""
    path = paths.repo_meeting_folder(meeting) / (repr(meeting) + suffix)

    # looking to prepend ".<suffix>" to ".ipynb", so you get: `.<suffix>.ipynb`
    assert suffix.startswith(".")

    try:
        nb = nbf.read(str(path), as_version=4)
    except FileNotFoundError:
        path.parent.mkdir(exist_ok=True)
        nb = nbf.v4.new_notebook()

    return nb, path


def update_or_create_folders_and_files(meeting: Meeting):
    """Performs some initial directory creation / cleanup. Currently this
    implementation is quite destructive. Ideally, there's some way to go about
    *intelligently* merging work ~ so this would allow for some temporary titles
    and the like.
    """
    repo_path = paths.repo_meeting_folder(meeting)
    site_path = paths.site_post(meeting)

    date = str(repo_path.stem)[:10]

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
                    old_workbook = match + Suffixes.WORKBOOK
                    new_workbook = repo_path.with_suffix(Suffixes.WORKBOOK)
                    (repo_path / old_workbook).rename(new_workbook)
                except FileNotFoundError:
                    pass

                try:
                    old_solution = match + Suffixes.SOLUTION
                    new_solution = repo_path.with_suffix(Suffixes.SOLUTION)
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


def update_or_create_notebook(meeting: Meeting, overwrite: bool = False):
    """Notebooks are the nuts and bolts of AI@UCF. These power the website's
    posts, our workshops, and are the general workbooks students can make use
    of.

    This function generates notebooks for a given meeting. *If the notebook
    exists*, a prompt will be issued for destructive actions. Otherwise, the
    notebook is strictly injected with the appropriate metadata and headings
    without losing content in the notebook.
    """
    # if not safety.can_overwrite(meeting, overwrite):
    #     return

    nb, path = read(meeting, suffix=Suffixes.SOLUTION)

    # region Enforce metadata and primary heading of notebooks
    try:
        # try to find the cell which has metadata of the form...
        #   ...
        #   "nb-title": true,
        #   ...
        # otherwise, set `title_index = None` so we have a set value
        title_index = (index for index, cell in enumerate(nb["cells"])
                       if cell["metadata"].get("nb-title", False))
        title_index = next(title_index, None)  # give `next()` a default
        del nb["cells"][title_index]
    except TypeError:
        # looks like the cell didn't exist, so let's move on
        pass

    # insert the heading as the first cell of the notebook
    nb["cells"].insert(0, _generate_heading(meeting))
    # assert that the needed metdata exists
    nb["metadata"].update(_generate_metadata(meeting))
    # write the notebook to disk
    nbf.write(nb, open(path, "w"))
    # endregion

    # region Setup `kernel-metadata.json` for Kaggle
    # strong preference to use `shutil`, but can't use with existing dirs
    # shutil.copytree(get_template("seed/meeting")), path.parent)
    copy_tree(get_template("seed/meeting"), str(path.parent))

    kernel_metadata_path = paths.repo_meeting_folder(meeting) / "kernel-metadata.json"
    kernel_metadata = Template(open(kernel_metadata_path).read())

    with open(kernel_metadata_path, "w") as f:
        meeting.optional["kaggle"]["competitions"].insert(0, kaggle.slug_competition(meeting))
        text = kernel_metadata.render(slug=kaggle.slug_kernel(meeting),
                                      notebook=repr(meeting),
                                      kaggle=meeting.optional["kaggle"])
        f.write(text.replace("'", '"'))  # JSON doesn't like single quotes
    # endregion

    # region Generate workbook by splitting solution manual
    # this was determined by looking at the `nbgrader` source code in checks for
    #   thie `ClearSolutions` Preprocessor
    nbgrader_cell_metadata = {
        "nbgrader": {
            "solution": True,
        }
    }

    for cell in nb["cells"]:
        if cell["cell_type"] is not "code":
            continue

        source = "".join(cell["source"])
        if Solution.BEGIN_FLAG in source and Solution.END_FLAG in source:
            cell["metadata"].update(nbgrader_cell_metadata)
        elif "nbgrader" in cell["metadata"]:
            del cell["metadata"]["nbgrader"]

    nbf.write(nb, open(path, "w"))

    workbook_exporter = nbc.NotebookExporter(
        preprocessors=[ClearSolutions, ClearOutput]
    )
    workbook, _ = workbook_exporter.from_notebook_node(nb)

    # this is a nightmare. we're going from `.solution.ipynb` to `.ipynb`, but
    #   have to remove the `.solution` suffix. which seems only doable by going
    #   down the entire tree of suffixes and removing them.
    workbook_path = path.with_suffix("").with_suffix("").with_suffix(Suffixes.WORKBOOK)
    with open(workbook_path, "w") as f_nb:
        f_nb.write(workbook)
    # endregion

def download_papers(meeting: Meeting):
    if not meeting.optional["papers"]:
        return

    folder = paths.repo_meeting_folder(meeting)

    for title, link in meeting.optional["papers"].items():
        with open(folder / f"{title}.pdf", "wb") as pdf:
            pdf.write(requests.get(link).content)


def render_banner(meeting: Meeting):
    """Generates the banner images for each meeting. These should be posted
       to the website as well as relevant social media.

    NOTE: This function is destructive. It will overwrite the banner it's
    generating - this is intentional behavior, ergo **do not edit banners
    directly**.
    """
    template_banner = Template(
        open(get_template("event-banner.html"), "r").read()
    )

    accepted_content_types = [
        f"image/{x}" for x in ["jpg", "jpeg", "png", "gif", "tiff"]
    ]

    extension = meeting.required["cover"].split(".")[-1]

    cover_image_path = paths.site_post_assets(meeting) / "cover.png"

    # snag the image from the URL provided in the syllabus
    cover = requests.get(meeting.required["cover"], headers={"user-agent": "Mozilla/5.0"})
    # use this to mute the EXIF data error ~ this seems to be a non-issue based
    #   on what I've read (@ionlights) ~ circa Sep/Oct 2019
    warnings.filterwarnings("ignore", "(Possibly )?corrupt EXIF data", UserWarning)
    if cover.headers["Content-Type"] in accepted_content_types:
        image_as_bytes = io.BytesIO(cover.content)
        try:
            # noinspection PyTypeChecker
            cover_as_bytes = io.BytesIO(open(cover_image_path, "rb").read())

            # get hashes to check for diff
            image_hash = sha256(image_as_bytes.read()).hexdigest()
            cover_hash = sha256(cover_as_bytes.read()).hexdigest()

            # clearly, something has changed between what we have and what
            #   was just downloaded -> update
            if cover_hash != image_hash:
                image = Image.open(image_as_bytes)
            else:
                image = Image.open(cover_as_bytes)
        except FileNotFoundError:
            image = Image.open(image_as_bytes)
        finally:
            image.save(cover_image_path)

    out = cover_image_path.with_name("banner.png")

    banner = template_banner.render(meeting=meeting,
                                    cover=cover_image_path.absolute())

    imgkit.from_string(banner, out, options={
        # standard flags should be passed as dict keys with empty values...
        "quiet": "",
        "debug-javascript": "",
        "enable-javascript": "",
        "javascript-delay": "400",
        "no-stop-slow-scripts": "",
    })


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
    nb, path = read(meeting, suffix=Suffixes.SOLUTION)

    # region Enforce metadata and primary heading of notebooks
    try:
        # try to find the cell which has metadata of the form...
        #   ...
        #   "nb-title": true,
        #   ...
        # otherwise, set `title_index = None` so you we can check to avoid
        title_index = (index for index, cell in enumerate(nb["cells"])
                       if cell["metadata"].get("nb-title", False))
        title_index = next(title_index, None)  # give `next()` a default
        del nb["cells"][title_index]
    except IndexError:
        # looks like the cell didn't exist, so let's move on
        pass

    autobot_metadata = nb["metadata"]["autobot"]
    # changes to the template should, honestly, be done in the `tpl` file below
    #   this is largely to make sure we don't have a fragile class, but at a
    #   later date, there might be reason to extract it to a class - especially
    #   for readability purposes
    md = nbc.MarkdownExporter()
    md.template_path = [get_template("notebooks", as_str=True)]
    md.template_file = "nb-front-matter"
    heading, _ = md.from_notebook_node(nb, resources={
        "metadata": autobot_metadata
       })

    html = nbc.HTMLExporter()
    html.template_path = [get_template("notebooks", as_str=True)]
    html.template_file = "nb-post-body"
    body, _ = html.from_notebook_node(nb)

    # NOTE: this is where the site's content path is generated
    output = paths.site_post(meeting) / f"{repr(meeting)}.md"
    output.parent.mkdir(exist_ok=True)

    with open(output, "w") as f:
        f.write(heading)
        f.write("\n{% raw %}")
        f.write(body)
        f.write("\n{% endraw %}")


def _generate_metadata(meeting: Meeting) -> Dict:
    return {
        "autobot": {
            "authors": [meeting.group.coords[c.lower()].as_metadata()
                        for c in meeting.required["instructors"]],
            "description": meeting.required["description"].strip(),
            "title": meeting.required["title"],
            "date": meeting.meta.date.isoformat()[:10],
            "tags": meeting.optional["tags"],
            "categories": [meeting.group.semester.short],
        }
    }


def _generate_heading(meeting: Meeting) -> nbf.NotebookNode:
    tpl_heading = Template(
        open(get_template("notebooks/nb-heading.html")).read()
    )

    tpl_args = {
        "group_sem": paths.repo_meeting_folder(meeting),
        "authors": [meeting.group.coords[author] for author in meeting.required["instructors"]],
        "title": meeting.required["title"],
        "file": meeting.required["filename"],
        "date": meeting.meta.date.isoformat()[:10]
    }

    rendering = tpl_heading.render(**tpl_args)
    head_meta = {"title": meeting.required["title"], "nb-title": True}

    return nbf.v4.new_markdown_cell(rendering, metadata=head_meta)
