from jinja2 import Template
import yaml

from admin import notebooks
from admin import res_semester as res


def gen_notebook(mode, semester, sched, year, workdir, nbs):
    for unit in yaml.load(open(sched, "r")):
        for meet in unit["list"]:
            nb_name = notebooks.nb_utils.name(meet, year)
            if mode is "make":
                workdir.joinpath(nb_name).mkdir(exist_ok=True)
            
            nbs[nb_name] = notebooks.N(nb_name, unit, meet, semester)
            eval("nbs[nb_name]._" + mode)()
            notebooks.nb_utils.write(nbs[nb_name])
      
            
import pathlib


def gen_jekyll_posts(semester, sched, year, workdir, nbs):
    docs = pathlib.Path("./docs")
    
    for unit in yaml.load(open(sched, "r")):
        for meet in unit["list"]:
            nb_name = notebooks.nb_utils.name(meet, year)
            
            nbs[nb_name] = notebooks.N(nb_name, unit, meet, semester)
            nbs[nb_name]._jekyll(docs)


def write_slurm(file):
    with open(res["templates"].joinpath("jupyter_notebooks.slurm"), "r") as f:
        tpl_slurm = Template(f.read())
    
    tpl_slurm_args = {}
    
    with open(file, "w") as f:
        f.write(tpl_slurm.render(**tpl_slurm_args))


def write_conda(file):
    with open(res["templates"].joinpath("semester.env.yml"), "r") as f:
        tpl_slurm = Template(f.read())
    
    tpl_slurm_args = {}
    
    with open(file, "w") as f:
        f.write(tpl_slurm.render(**tpl_slurm_args))


import datetime as dt
import numpy as np
import pandas as pd


def which():
    t = dt.date.today()
    
    def dateme(mmdd_st: str, mmdd_ed: str):
        stmo = int(mmdd_st.split("-")[0])
        edmo = int(mmdd_ed.split("-")[0])
        
        if stmo < edmo:
            return np.arange(f'{t.year - 0}-{mmdd_st}',
                             f'{t.year + 0}-{mmdd_ed}',
                             dtype='datetime64[D]')
        elif t.month <= edmo:
            return np.arange(f'{t.year - 1}-{mmdd_st}',
                             f'{t.year + 0}-{mmdd_ed}',
                             dtype='datetime64[D]')
        
        return np.arange(f'{t.year - 0}-{mmdd_st}',
                         f'{t.year + 1}-{mmdd_ed}',
                         dtype='datetime64[D]')
    
    # "su" commented out b/c we don't do summer meetings, at least for now
    splits = {
        "sp": dateme("12-08", "05-07"),
        # "su": dateme("05-08", "08-07"),
        "fa": dateme("08-08", "12-07"),
    }
    
    key = None
    for key, val in splits.items():
        if t in val:
            break
    
    return key + pd.to_datetime(splits[key][-1]).strftime("%y")
