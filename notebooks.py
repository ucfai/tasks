"""This module generates the template-ized Jupyter Notebooks we used for every
lecture and adds in metadata to be used when converting given Notebooks into
corresponding HTML to be posted on the web.
"""

__author__ = "John Muchovej <j+sigai@ionlights.org>"
__maintainer__ = "SIGAI@UCF, <admins@ucfsigai.org>"
__version__ = "0.1"

import datetime as dt
from pathlib import Path

import nbformat as nbf

import nb_utils

from nbconvert import HTMLExporter


class Notebook:
    def __init__(self, name_, unit_, meet_, sem_):
        self.sem = Path(sem_)
        self.name = Path(name_).joinpath(name_ + ".ipynb")
        self.unit = unit_
        self.meet = meet_
        self.date = dt.date(
                **{k: v
                   for k, v in zip(["year", "month", "day"],
                                   map(int, name_.split("-")[:3]))
                   })
        
        self.nb = None
    
    def _make(self):
        try:
            self.nb = nbf.read(str(self.sem.joinpath(self.name)), as_version=4)
            reading = True
        except FileNotFoundError:
            reading = False
            self.nb = nbf.v4.new_notebook()
        
        self.nb["metadata"] = nb_utils.metadata(self.date, self.meet, self.unit)
        if not reading:
            self.nb["cells"].append(nb_utils.heading(self.nb, self.date, self.meet))
        else:
            idx = next((idx
                        for idx, cell in enumerate(self.nb["cells"])
                        if cell["metadata"]["type"] == "sigai_heading")
                       , None)
            self.nb["cells"][idx] = nb_utils.heading(self.nb, self.date, self.meet)
        
        self.name = self.sem.joinpath(self.name)
    
    def _update(self):
        self.nb = nbf.read(str(self.sem.joinpath(self.name)), as_version=4)
        
        self.nb["metadata"] = nb_utils.metadata(self.date, self.meet, self.unit)
        
        idx = next((idx
                    for idx, cell in enumerate(self.nb["cells"])
                    if cell["metadata"]["type"] == "sigai_heading")
                   , None)
        self.nb["cells"][idx] = nb_utils.heading(self.nb, self.date, self.meet)

        self.name = self.sem.joinpath(self.name)
    
    def _jekyll(self, outdir):
        # nbconv_tpl = pathlib.Path(res["templates"]).joinpath("sigai-markdown.tpl")
        self.nb = nbf.read(str(self.sem.joinpath(self.name)), as_version=4)
        
        html = HTMLExporter()
        html.template_file = "basic"
        
        sigai = self.nb["metadata"]["sigai"]
        
        idx = next((idx
                    for idx, cell in enumerate(self.nb["cells"])
                    if cell["metadata"]["type"] == "sigai_heading")
                   , None)
        
        del self.nb["cells"][idx]
        
        body, _ = html.from_notebook_node(self.nb)
        
        outdir.joinpath("_posts").joinpath(self.name).parent.mkdir(exist_ok=True)
        output = outdir.joinpath("_posts").joinpath(self.name.with_suffix(".md"))
        with open(output, "w") as f:
            f.write("---\n")
            f.write(f"title: \"{sigai['title']}\"\n")
            f.write(f"categories: [\"{str(self.sem)}\"]\n")
            f.write(f"tags: {[sigai['unit']['name']]}\n")
            f.write(f"authors: {[_['github'] for _ in sigai['authors']]}\n")
            f.write(f"description: >\n  \"{sigai['description']}\"\n")
            f.write("---\n")
            f.write(body)
