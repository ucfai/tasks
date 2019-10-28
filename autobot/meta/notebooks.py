import io
import os
import datetime
import hashlib
import shutil
from distutils.dir_util import copy_tree
from pathlib import Path
from typing import List, Dict
from itertools import product

import imgkit
import requests
import yaml
from PIL import Image
import pandas as pd
from jinja2 import Template
import nbformat as nbf
import nbconvert as nbc
from nbgrader.preprocessors import ClearSolutions, ClearOutput

from autobot import ORG_NAME
from autobot.lib.configs import website

from .group import Group
from .meeting import Meeting


src_dir = Path(__file__).parent.parent


class Suffixes:
    SOLUTION = ".solution.ipynb"
    RELEASE = ".ipynb"


def read(group: Group, meeting: Meeting, suffix: str = ""):
    path = group.as_dir() / meeting.as_nb()

    if suffix:
        suffix = f".{suffix}" if not suffix.startswith(".") else suffix
        path = path.with_suffix(suffix + path.suffix)

    try:
        nb = nbf.read(f"{path}", as_version=4)
    except FileNotFoundError:
        path.parent.mkdir(exist_ok=True)
        nb = nbf.v4.new_notebook()

    return nb, path


def write(group: Group, meeting: Meeting):
    # creating a solution notebook
    nb, path = read(group, meeting, suffix="solution")

    title_index = next(
        (
            index
            for index, cell in enumerate(nb["cells"])
            if cell["metadata"].get("nb-title", False)
        ),
        None,
    )

    if title_index is not None:
        del nb["cells"][title_index]

    nb["cells"].insert(0, _generate_heading(meeting, str(group.as_dir())))
    nb["metadata"].update(_generate_metadata(group, meeting))

    with open(path, "w") as f_nb:
        nbf.write(nb, f_nb)

    # strong preference to use `shutil`, but can't use with existing dirs
    # shutil.copytree(src_dir / "templates/seed/meeting", path.parent)
    copy_tree(str(src_dir / "templates/seed/meeting"), str(path.parent))

    with open(path.parent / "kernel-metadata.json", "r") as f:
        kernel_metadata = Template(f.read())

    with open(path.parent / "kernel-metadata.json", "w") as f:
        title_as_slug = f"{group.name.lower()}-{group.sem.short}-{meeting.filename}"

        meeting.kaggle["competitions"].insert(0, f"{ORG_NAME}-{title_as_slug}")
        text = kernel_metadata.render(
            slug=title_as_slug, notebook=repr(meeting), kaggle=meeting.kaggle
        )

        f.write(text.replace("'", '"'))  # JSON doesn't like single-quotes


def as_post(meeting: Meeting):
    # TODO: combine this into a single exporter
    nb = meeting.read_nb(suffix=Suffixes.SOLUTION)

    title_index = next(
        (
            index
            for index, cell in enumerate(nb["cells"])
            if cell["metadata"].get("nb-title", False)
        ),
        None,
    )

    if title_index is not None:
        del nb["cells"][title_index]

    autobot_metadata = nb["metadata"]["autobot"]
    # changes to the template should, honestly, be done in the `tpl` file below
    #   this is largely to make sure we don't have a fragile class, but at a
    #   later date, there might be reason to extract it to a class - especially
    #   for readability purposes
    md = nbc.MarkdownExporter()
    md.template_path = [str(src_dir / "templates/notebooks")]
    md.template_file = "nb-front-matter"
    heading, _ = md.from_notebook_node(nb, resources={"metadata": autobot_metadata})

    html = nbc.HTMLExporter()
    html.template_path = [str(src_dir / "templates/notebooks")]
    html.template_file = "nb-post-body"
    body, _ = html.from_notebook_node(nb)

    # NOTE: this is where the site's content path is generated
    output = SiteUtils.post_path(meeting) / f"{repr(meeting)}.md"

    SiteUtils.post_path(meeting).mkdir(exist_ok=True)

    with open(output, "w") as f:
        f.write(heading)
        f.write("\n{% raw %}")
        f.write(body)
        f.write("\n{% endraw %}")


def split_nb(meeting: Meeting):
    nb = meeting.read_nb(suffix=Suffixes.SOLUTION)

    # this was determined by looking at the nbgrader source in the checks for
    #   the ClearSolutions preprocessor
    nbgrader_cell_metadata = {"nbgrader": {"solution": True}}

    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            cell["metadata"].update(nbgrader_cell_metadata)

    with open(meeting.repo_path.with_suffix("ipynb"), "w") as f_nb:
        nbf.write(nb, f_nb)

    nb_exporter = nbc.NotebookExporter(preprocessor=[ClearSolutions, ClearOutput])
    nb_empty, _ = nb_exporter.from_notebook_node(nb)

    nb_release = path.with_suffix("").with_suffix("").with_suffix(path.suffixes[-1])
    with open(nb_release, "w") as f_nb:
        f_nb.write(nb_empty)


def make_banner(meeting: Meeting):
    pass
