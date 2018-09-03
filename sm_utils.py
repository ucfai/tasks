from string import Template
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
      
      
import imgkit

def gen_banners(semester, sched, year, workdir, nbs):
    banner = Template(open(res["templates"].joinpath("banner.html"), "r"))
    syllabus = yaml.load(open(sched, "r"))

    banner_args = {
        "weekday": syllabus["week_day"],
        "time": syllabus["meet_time"],
        "room": syllabus["room"],
        "date": None,
        "title": None,
        "cover": None,
    }
    for unit in syllabus["list"]:
        for meet in unit["list"]:
            nb_name = nb_utils.name(meet, year)
            out = workdir.joinpath(nb_name).joinpath("banner.jpg")
            res = requests.get(meet["cover"], stream=True)

            ext = imghdr.what(h=res.raw)

            cov = workdir.joinpath(nb_name).joinpath("cover." + ext)

            with open(cov, "wb") as f:
                shutil.copyfileobj(res.raw, f)

            mm, dd = map(int, meet["date"].split("/"))
            banner_args["date"] = dt.date(year, mm, dd).strftime("%b %d")
            banner_args["title"] = meet["name"]
            banner_args["cover"] = meet["cover"]

            banner_ = banner.substitute(**banner_args)
            imgkit.from_string(banner_, out)
    pass

            
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
