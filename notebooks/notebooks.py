import datetime as dt
from pathlib import Path

import nbformat as nbf

from . import nb_utils


class Notebook:
    def __init__(self, name_, unit_, meet_):
        self.name = Path(name_).joinpath(name_ + ".ipynb")
        self.unit, self.meet = unit_, meet_
        self.date = dt.date(
                **{k: v
                   for k, v in zip(["year", "month", "day"],
                                   self.name.split("-")[:3])
                   })
        
        self.nb = None
    
    def _make(self):
        self.nb = nbf.v4.new_notebook()
        
        self.nb["metadata"] = nb_utils.metadata(self.date, self.meet, self.unit)
        self.nb["cells"].append(nb_utils.heading(self.nb, self.date, self.meet))
    
    def _update(self):
        self.nb = nbf.read(str(self.name), as_version=4)
        
        self.nb["metadata"] = nb_utils.metadata(self.date, self.meet, self.unit)
        
        idx = next((idx
                    for idx, cell in self.nb["cells"]
                    if cell["metadata"]["type"] is "sigai_heading")
                   , None)
        self.nb["cells"][idx] = nb_utils.heading(self.nb, self.date, self.meet)
    
    def _jekyll(self):
        pass
