"""This module generates the template-ized Jupyter Notebooks we used for every lecture and adds in metadata to be used when converting given Notebooks into corresponding HTML to be posted on the web.
"""

__author__ = "John Muchovej <j+sigai@ionlights.org>"
__maintainer__ = "SIGAI@UCF, <admins@ucfsigai.org>"
__version__ = "0.1"

from pathlib import Path
from jinja2 import Template
from PIL import Image

from admin import utils
from admin import notebooks
from admin.notebooks import Notebook

import numpy as np
import pandas as pd

import datetime as dt
import io
import logging
import shutil

import yaml
import imgkit
import requests

ErrFoundFile = Template("Found `{{ name }}/{{ file }}`. Let's not continue, to "
                        "avoid overriding.")
ErrNotFoundFile = Template("Couldn't find `{{ name }}/{{ file }}`. Please "
                           "restart from `make` command - NOTE this overwrites "
                           "any changes you may have made.")

SuccessTouchd = Template("Successfully touch'd `{{ name }}/{{ file }}`.")


class Semester:
    coordinators = None
    
    def __init__(self, cwd):
        self.name = which()
        self.year = int("20" + self.name[-2:])
        
        self.workdir = Path(cwd).joinpath(self.name)
        if self.workdir.is_dir():
            msg = f"Uhh... looks like `{self.name}` already exists. Tread " \
                  "carefully."
            logging.warning(msg)
            print(msg)
        else:
            self.workdir.mkdir()
        
        self._file_sched = self.workdir.joinpath("syllabus.yml")
        self._file_admin = self.workdir.joinpath("coordinators.yml")
        self._file_conda = self.workdir.joinpath(self.name + ".env.yml")
        self._file_slurm = self.workdir.joinpath("jupyter_notebooks.slurm")
        
        self.admin = yaml.load(open(self._file_admin, "r"))
        syllabus = yaml.load(open(self._file_sched, "r"))
        self.meet_day  = syllabus["meet_day" ]
        self.meet_room = syllabus["meet_room"]
        self.meet_time = syllabus["meet_time"]
        self.sched = syllabus["teach"]
        
        self.notebooks = {}
    
    def make(self, call_):
        if call_ is not "jekyll_posts":
            self.__validate_skeleton_presence(prepnbs=(call_ in ["skeleton", "notebooks"]))
            
        calls = {
            "skeleton"    : self.__make_skeleton,
            "notebooks"   : self.__make_notebooks,
            "jekyll_posts": self.__make_jekyll_posts,
            "banners"     : self.__make_banners,
        }
        
        calls[call_]()
        
    def update(self, call_, specific=None):
        calls = {
            "skeleton" : self.__update_skeleton,
            "notebooks": self.__update_notebooks,
        }
    
        if specific is not None:
            calls[call_](specific)
        else:
            calls[call_]()
    
    def __make_skeleton(self):
        name = self.name
        
        file = self._file_sched.name
        shutil.copyfile(utils.res_gen("sem", file), self._file_sched)
        logging.info(SuccessTouchd.render(name=name, file=file))
        
        file = self._file_admin.name
        shutil.copyfile(utils.res_gen("sem", file), self._file_admin)
        logging.info(SuccessTouchd.render(name=name, file=file))
        
        file = self._file_conda.name
        self.__write_file("slurm", file)
        
        file = self._file_slurm.name
        self.__write_file("slurm", file)
    
    def __make_notebooks(self):
        self.__gen_notebook("make")
    
    def __make_jekyll_posts(self):
        # docs = Path("./docs")
        
        self.__gen_notebook("jekyll")
    
    def __make_banners(self):
        banner = Template(open(utils.res_gen("sem", "event-banner.html"), "r").read())
        
        banner_args = {
            "weekday": self.meet_day,
            "time"   : self.meet_time,
            "room"   : self.meet_room,
            "date"   : None,
            "title"  : None,
            "cover"  : None,
        }
        
        accepted = {"jpeg": "jpg", "png": "png", "gif": "gif", "tiff": "tif"}
        
        for unit in self.sched:
            for meet in unit["list"]:
                nb_name = notebooks.name(meet, self.year)
                logging.info(f"generating {nb_name} banner.jpg")
                out = self.workdir.joinpath(nb_name).joinpath("banner.jpg")
                
                mm, dd = map(int, meet["date"].split("/"))
                banner_args["date"] = dt.date(self.year, mm, dd).strftime("%b %d")
                banner_args["title"] = meet["name"].encode('ascii', 'xmlcharrefreplace').decode("utf-8")
                
                cov_exists = False
                for ext in accepted.values():
                    cov = self.workdir.joinpath(nb_name).joinpath("cover." + ext)
                    if cov.exists():
                        cov_exists = True
                        break
                
                if not cov_exists and meet["covr"] is not "":
                    res = requests.get(meet["covr"])
                    if res.status_code != requests.codes.ok:
                        res = requests.get(meet["covr"], headers={"user-agent": "Mozilla/5.0"})
                    
                    img = Image.open(io.BytesIO(res.content))
                    fmt = img.format.lower()
                    if fmt in accepted.keys() and res.status_code == requests.codes.ok:
                        cov = self.workdir.joinpath(nb_name).joinpath("cover." + accepted[fmt])
                        img.save(str(cov))
                
                banner_args["cover"] = cov if meet["covr"] is not "" else ""
                
                banner_ = banner.render(banner_args)
                imgkit.from_string(banner_, out, options={"quiet": ""})
    
    def __update_notebooks(self):
        self.__gen_notebook("update")
        
    def __update_skeleton(self):
        pass
    
    def __validate_skeleton_presence(self, prepnbs=False):
        files = [self._file_sched, self._file_admin]
        for file in files:
            existence = (not file.exists()) or (prepnbs and file.exists())
            if not existence:
                ErrFoundFile.render(name=self.name, file=file.name)
        
        if not prepnbs:
            files = [self._file_conda, self._file_slurm]
            for file in files:
                if not file.exists():
                    ErrFoundFile.render(name=self.name, file=file.name)
    
    def __gen_notebook(self, mode):
        for unit in self.sched:
            for meet in unit["list"]:
                nb_name = notebooks.name(meet, self.year)
                if mode != "jekyll":
                    self.workdir.joinpath(nb_name).mkdir(exist_ok=True)

                coords = {gh: v["nam"] for gh, v in self.admin.items() if gh in meet["inst"]}
                self.notebooks[nb_name] = Notebook(nb_name, unit, meet, self.name, coords)
                self.notebooks[nb_name].call(mode)
                if mode != "jekyll":
                    self.notebooks[nb_name].write()
                
    def __write_file(self, lookup, file):
        def slurm(file):
            with open(utils.res_gen("sem", "jupyter_notebooks.slurm"), "r") as f:
                tpl_slurm = Template(f.read())
        
            tpl_slurm_args = {}
        
            with open(file, "w") as f:
                f.write(tpl_slurm.render(**tpl_slurm_args))
    
        def conda(file):
            with open(utils.res_gen("sem", "semester.env.yml"), "r") as f:
                tpl_conda = Template(f.read())
        
            tpl_conda_args = {}
        
            with open(file, "w") as f:
                f.write(tpl_conda.render(**tpl_conda_args))
                
        eval(lookup)(file)

        logging.info(SuccessTouchd.render(name=self.name, file=file))


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
