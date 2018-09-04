"""This module generates the template-ized Jupyter Notebooks we used for every
lecture and adds in metadata to be used when converting given Notebooks into
corresponding HTML to be posted on the web.
"""
import shutil

__author__ = "John Muchovej <j+sigai@ionlights.org>"
__maintainer__ = "SIGAI@UCF, <admins@ucfsigai.org>"
__version__ = "0.1"

from pathlib import Path

from nbconvert import HTMLExporter

import nbformat as nbf

from jinja2 import Template
import datetime as dt


class Notebook:
    def __init__(self, name_, unit_, meet_, sem_, coordinators_):
        self.sem = Path(sem_)
        self.path = Path(name_)
        self.filename = Path(name_).joinpath(name_ + ".ipynb")
        self.unit = unit_
        self.meet = meet_
        self.date = dt.date(
                **{k: v
                   for k, v in zip(["year", "month", "day"],
                                   map(int, name_.split("-")[:3]))
                   })
        
        self.lecturers = coordinators_
        
        self.nb = None
    
    def call(self, call_, outdir=None):
        calls = {
            "make"  : self.__make,
            "update": self.__update,
            "jekyll": self.__jekyll,
        }
        
        if outdir is not None:
            calls[call_](outdir=outdir)
        else:
            calls[call_]()
    
    def __make(self):
        try:
            self.nb = nbf.read(str(self.sem.joinpath(self.filename)), as_version=4)
            reading = True
        except FileNotFoundError:
            reading = False
            self.nb = nbf.v4.new_notebook()
        
        self.nb["metadata"] = metadata(self.date, self.meet, self.unit, self.lecturers)
        if not reading:
            self.nb["cells"].append(heading(self.nb, self.date, self.meet))
        else:
            idx = next((idx
                        for idx, cell in enumerate(self.nb["cells"])
                        if cell["metadata"]["type"] == "sigai_heading")
                       , None)
            self.nb["cells"][idx] = heading(self.nb, self.date, self.meet)
        
        self.filename = self.sem.joinpath(self.filename)
    
    def __update(self):
        self.__make()
    
    def __jekyll(self, outdir=Path("./docs")):
        # nbconv_tpl = utils.res_gen("ntbk", "sigai-markdown.tpl")
        self.nb = nbf.read(str(self.sem.joinpath(self.filename)), as_version=4)
        
        html = HTMLExporter()
        html.template_file = "basic"
        
        sigai = self.nb["metadata"]["sigai"]
        
        idx = next((idx
                    for idx, cell in enumerate(self.nb["cells"])
                    if cell["metadata"]["type"] == "sigai_heading")
                   , None)
        
        del self.nb["cells"][idx]
        
        body, _ = html.from_notebook_node(self.nb)
        
        post_folder = outdir.joinpath("_posts").joinpath(self.filename).parent
        post_folder.mkdir(exist_ok=True)

        shutil.copyfile(self.sem.joinpath(self.path).joinpath("banner.jpg"),
                        post_folder.joinpath("banner.jpg"))
        
        output = outdir.joinpath("_posts").joinpath(self.filename.with_suffix(".md"))
        with open(output, "w") as f:
            f.write("---\n")
            f.write(f"title: \"{sigai['title']}\"\n")
            f.write(f"categories: [\"{str(self.sem)}\"]\n")
            f.write(f"tags: {[sigai['unit']['name']]}\n")
            f.write(f"authors: {[_['github'] for _ in sigai['authors']]}\n")
            f.write(f"description: >\n  \"{sigai['description']}\"\n")
            f.write("---\n")
            f.write(body)
    
    def write(self):
        assert self.nb is not None, "Looks like I'm a non-existent Notebook! :o"
        with open(self.filename, "w") as _:
            nbf.write(self.nb, _)


nb_heading = Template("""# {{title}}
---
by: {{ authors }}, on {{ date }}
""")
author_templ = Template("{{ name }} \([@{{ gh }}](github.com/{{ gh }}/)\)")


def heading(nb, date, meet):
    author_tuple = [(a["name"], a["github"])
                    for a in nb["metadata"]["sigai"]["authors"]]
    
    curr_nb_heading = nb_heading.render(
        title=meet["name"],
        authors=", ".join(
                [author_templ.render(name=inst, gh=git)
                 for inst, git in author_tuple]),
        date=date.strftime("%m %b %Y"),
    )
    
    curr_nb_metadata = {
        "name": meet["name"],
        "type": "sigai_heading"
    }
    
    return nbf.v4.new_markdown_cell(curr_nb_heading,
                                    metadata=curr_nb_metadata)


def metadata(date, meet, unit, lecturers):
    return {
        "sigai": {
            "authors"    : [
                {
                    "github": gh,
                    "name"  : name
                } for gh, name in lecturers.items()
            ],
            "description": meet["desc"].strip(),
            "title"      : meet["name"],
            "date"       : date.isoformat(),
            "unit"       : {
                "name"  : unit["name"],
                "number": unit["unit"]
            }
        }
    }


def name(entry, year):
    mm, dd = map(int, entry["date"].split("/"))
    
    return "-".join([str(dt.date(year, mm, dd)), entry["file"]])
