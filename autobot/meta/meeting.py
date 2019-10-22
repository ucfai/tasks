import io
import os
import copy
import datetime
import shutil
import subprocess
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
from jinja2 import Template
import nbformat as nbf
import nbconvert as nbc
from nbgrader.preprocessors import ClearSolutions, ClearOutput

from autobot import ORG_NAME
from autobot.lib.utils import website

from . import MeetingMeta
from .coordinator import Coordinator
from .group import Group

src_dir = Path(__file__).parent.parent


class Meeting:
    def __init__(self, group: Group, meeting_dict: Dict, meta: MeetingMeta):
        assert set(["required", "optional"]).intersection(set(meeting_dict.keys()))

        self.group = group
        self.required = meeting_dict["required"]
        self.optional = meeting_dict["optional"]

        if "date" in self.optional and self.optional["date"]:
            date = self.optional["date"]
        else:
            date = meta.date

        if "room" in self.optional and self.optional["room"]:
            room = self.optional["room"]
        else:
            room = meta.room

        self.meta = MeetingMeta(date, room)

        self.required["instructors"] = [x.lower()
                                        for x in self.required["instructors"]]

        for key in self.required.keys():
            assert self.required[key], \
                f"You haven't specified `{key}` for this meeting..."

        self.repo_path = self.group.as_dir() / repr(self)
        self.site_path = (website.CONTENT_DIR / self.group.as_dir(for_jekyll=True) /
                          "_posts" / repr(self))

        self.repo_path.mkdir(exist_ok=True)
        self.site_path.mkdir(exist_ok=True)

    def write_yaml(self) -> Dict:
        """This prepares the dict to write each entry in `syllabus.yml`."""
        return {
            "required": {
                "title": self.title,
                "cover": self.cover,
                "filename": self.filename,
                "instructors": self.instructors,
                "datasets": self.datasets,
                "description": self.description,
            },
            "optional": {
                "date": self.meta.date,
                "room": self.meta.room,
                "tags": self.tags,
                "slides": self.slides,
                "kernels": self.kernels,
                "papers": self.papers
            }
        }

    @staticmethod
    def parse_yaml(d: Dict, coords: Dict, meta: MeetingMeta) -> Dict:
        """This method consumes a dict which will be used to see a given
        `Meeting` instance, thus allowing for usage elsewhere.

        :param d: Dict
        :param coords: Dict
        :param meta: MeetingMeta

        :return Dict
        """
        for k, v in d["required"].items():
            assert v, f"You haven't specified `{k}` in one of the syllabi entries..."

        d["required"]["instructors"] = list(map(lambda x: coords[x.lower()],
                                                d["required"]["instructors"]))
        d["meta"] = meta

        if d["optional"]["room"]:
            d["meta"]["room"] = d["optional"]["room"]

        if d["optional"]["date"]:
            d["meta"]["date"] = d["optional"]["date"]

        return d

    def as_md(self): return self.__as_path(ext="md")
    def as_dir(self): return self.__as_path(ext="")
    def fqd_path(self): return self.group.as_dir() / self.as_dir().parent
    def as_slug_competition(self):
        return f"{ORG_NAME}-{self.as_slug_kernel()}"
    def as_slug_kernel(self):
        return f"{self.group.for_kaggle()}-{self.required['filename']}"

    def __as_path(self, ext: str = ""):
        if ext and "." != ext[0]:
            ext = f".{ext}"
        return Path(f"{repr(self)}/{repr(self)}{ext}")

    def __repr__(self):
        if not self.meta.date:
            raise ValueError("`Meeting.date` must be defined for this to work.")
        return f"{self.meta.date.isoformat()[:10]}-{self.required['filename']}"

    def __str__(self): return self.title
    def __lt__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date < other.meta.date

    def __le__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date <= other.meta.date

    def __ge__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date >= other.meta.date

    def __gt__(self, other) -> bool:
        assert type(other) == type(self)
        return self.meta.date > other.meta.date

    def __can_overwrite(self, overwrite: bool):
        if overwrite:
            return True

        if self.repo_path.exists():
            overwrite = input(f"`{self.repo_path}` exists. Overwrite? [y/N] ")
            return overwrite.lower() in ["y", "yes"]

        return False

    def __read_nb(self, suffix: str = ""):
        path = copy.deepcopy(self.repo_path) / (repr(self) + ".ipynb")
        # looking to prepend ".suffix" to ".ipynb", so you get: `.suffix.ipynb`
        if suffix:
            suffix = suffix if suffix.startswith(".") else f".{suffix}"
            path = path.with_suffix(suffix + path.suffix)

        try:
            nb = nbf.read(str(path), as_version=4)
        except FileNotFoundError:
            path.parent.mkdir(exist_ok=True)
            nb = nbf.v4.new_notebook()

        return nb, path

    def as_notebook(self, overwrite: bool = False):
        if not self.__can_overwrite(overwrite):
            return

        nb, path = self.__read_nb(suffix="solution")

        # region Enforce metadata and primary heading of notebooks
        title_index = next((index for index, cell in enumerate(nb["cells"])
                            if cell["metadata"].get("nb-title", False)), None)

        if title_index is not None:
            del nb["cells"][title_index]

        nb["cells"].insert(0, _generate_heading(self))
        nb["metadata"].update(_generate_metadata(self))

        with open(path, "w") as f_nb:
            nbf.write(nb, f_nb)
        # endregion

        # region Setup `kernel-metadata.json` for Kaggle
        # strong preference to use `shutil`, but can't use with existing dirs
        # shutil.copytree(src_dir / "templates/seed/meeting", path.parent)
        copy_tree(str(src_dir / "templates/seed/meeting"), str(path.parent))

        with open(self.repo_path / "kernel-metadata.json", "r") as f:
            kernel_metadata = Template(f.read())

        with open(self.repo_path / "kernel-metadata.json", "w") as f:
            self.optional["kaggle"]["competitions"].insert(0, self.as_slug_competition())
            text = kernel_metadata.render(slug=self.as_slug_kernel(),
                                          notebook=repr(self),
                                          kaggle=self.optional["kaggle"])

            f.write(text.replace("'", '"'))  # JSON doesn't like single-quotes
        # endregion

        # region Split notebooks from solution manual
        # this was determined by looking at the nbgrader source in the checks for
        #   the ClearSolutions preprocessor
        nbgrader_cell_metadata = {
            "nbgrader": {
                "solution": True,
            }
        }

        solution_begin = "### BEGIN SOLUTION"
        solution_end   = "### END SOLUTION"

        for cell in nb["cells"]:
            if cell["cell_type"] != "code":
                continue

            source = "".join(cell["source"])
            if solution_begin in source and solution_end in source:
                cell["metadata"].update({"nbgrader": {"solution": True}})
            elif "nbgrader" in cell["metadata"]:
                del cell["metadata"]["nbgrader"]

        with open(path, "w") as f_nb:
            nbf.write(nb, f_nb)

        nb_exporter = nbc.NotebookExporter(preprocessors=[ClearSolutions, ClearOutput])
        nb_empty, _ = nb_exporter.from_notebook_node(nb)

        nb_release = path.with_suffix("").with_suffix("").with_suffix(path.suffixes[-1])
        with open(nb_release, "w") as f_nb:
            f_nb.write(nb_empty)
        # endregion

    def as_post(self, overwrite: bool = False):
        if not self.__can_overwrite(overwrite):
            return

        nb, path = self.__read_nb(suffix="solution")
        title_index = next((index for index, cell in enumerate(nb["cells"])
                            if cell["metadata"].get("nb-title", False)), None)

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
        heading, _ = md.from_notebook_node(nb, resources={
            "metadata": autobot_metadata
           })

        html = nbc.HTMLExporter()
        html.template_path = [str(src_dir / "templates/notebooks")]
        html.template_file = "nb-post-body"
        body, _ = html.from_notebook_node(nb)

        # NOTE: this is where the site's content path is generated
        output = (website.CONTENT_DIR / self.group.as_dir(for_jekyll=True) / "_posts" /
                  repr(self) / f"{repr(self)}.md")

        output.parent.mkdir(exist_ok=True)

        with open(output, "w") as f:
            f.write(heading)
            f.write("\n{% raw %}")
            f.write(body)
            f.write("\n{% endraw %}")

    def as_banner(self, overwrite: bool = False):
        """Generates the banner images for each meeting. These should be posted
        to the website as well as relevant social media."""
        if not self.__can_overwrite(overwrite):
            return

        template_banner = Template(
            open(src_dir / "templates/event-banner.html", "r").read()
        )

        accepted_content_types = [
            f"image/{x}" for x in ["jpg", "jpeg", "png", "gif", "tiff"]
        ]

        extension = self.required["cover"].split(".")[-1]

        cover_image_path = (website.CONTENT_DIR /
                            self.group.as_dir(for_jekyll=True) / "_posts" /
                            repr(self) / "cover.png")

        # snag the image from the URL provided in the syllabus
        cover = requests.get(self.required["cover"], headers={"user-agent": "Mozilla/5.0"})
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

        banner = template_banner.render(meeting=self,
                                        cover=cover_image_path.absolute())

        imgkit.from_string(banner, out, options={
            # standard flags should be passed as dict keys with empty values...
            # "quiet": "",
            "debug-javascript": "",
            "enable-javascript": "",
            "javascript-delay": "400",
            "no-stop-slow-scripts": "",
        })


    def publish_kaggle(self):
        print(self.fqd_path(), os.getcwd())
        if "KAGGLE_CONFIG_DIR" not in os.environ:
            os.environ["KAGGLE_CONFIG_DIR"] = str(Path(__file__).parent.parent.parent)

        cwd = os.getcwd()
        os.chdir(self.fqd_path())
        import pdb; pdb.set_trace()
        subprocess.call("kaggle k push", shell=True)
        os.chdir(cwd)

def _generate_metadata(meeting: Meeting) -> Dict:
    return {
        "autobot": {
            "authors": [meeting.group.coords[c.lower()].as_metadata()
                        for c in meeting.required["instructors"]],
            "description": meeting.required["description"].strip(),
            "title": meeting.required["title"],
            "date": meeting.meta.date.isoformat()[:10],  # outputs as 2018-01-16
            "tags": meeting.optional["tags"],
            "categories": [meeting.group.sem.short],
        }
    }


def _generate_heading(meeting: Meeting) -> nbf.NotebookNode:
    tpl_heading = Template(
        open(src_dir / "templates/notebooks/nb-heading.html").read()
    )

    tpl_args = {
        "group_sem": meeting.group.as_dir(),
        "authors": [meeting.group.coords[author] for author in meeting.required["instructors"]],
        "title": meeting.required["title"],
        "file": meeting.required["filename"],
        "date": meeting.meta.date.isoformat()[:10]
    }

    rendering = tpl_heading.render(**tpl_args)
    head_meta = {"title": meeting.required["title"], "nb-title": True}

    return nbf.v4.new_markdown_cell(rendering, metadata=head_meta)
