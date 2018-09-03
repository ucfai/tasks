"""This module generates the template-ized Jupyter Notebooks we used for every lecture and adds in metadata to be used when converting given Notebooks into corresponding HTML to be posted on the web.
"""

__author__ = "John Muchovej <j+sigai@ionlights.org>"
__maintainer__ = "SIGAI@UCF, <admins@ucfsigai.org>"
__version__ = "0.1"

from pathlib import Path
import logging

from admin import sm_utils

import shutil
import yaml

ErrFoundFile = "Found `{name}/{file}`. Let's not continue, to avoid overriding."
ErrNotFoundFile = "Couldn't find `{name}/{file}`. Please restart from " \
                  "`make` command - NOTE this overwrites any changes you may " \
                  "have made."

SuccessTouchd = "Successfully touch'd `{name}/{file}`."


class Semester:
    coordinators = None
    
    def __init__(self, cwd):
        self.name = sm_utils.which()
        self.year = int("20" + self.name[-2:])
        
        self.workdir = Path(cwd).joinpath(self.name)
        if self.workdir.is_dir():
            msg = "Uhh... looks like `{}` already exists. Tread " \
                  "carefully.".format(self.name)
            logging.warning(msg)
            print(msg)
        else:
            self.workdir.mkdir()

        self.file_sched = self.workdir.joinpath("syllabus.yml")
        self.file_admin = self.workdir.joinpath("coordinators.yml")
        self.file_conda = self.workdir.joinpath(self.name + ".env.yml")
        self.file_slurm = self.workdir.joinpath("jupyter_notebooks.slurm")
        
        self.notebooks = {}
        
        self.gen_nb_args = {
            "semester": self.name,
            "nbs"     : self.notebooks,
            "year"    : self.year,
            "workdir" : self.workdir,
            "sched"   : self.file_sched,
        }


def make_skeleton(semester):
    validate_skeleton_presence(semester)
    
    name = semester.name
    
    file = semester.file_sched.name
    shutil.copyfile(res["templates"].joinpath(file), semester.file_sched)
    logging.info(SuccessTouchd.format(name=name, file=file))
    
    file = semester.file_admin.name
    shutil.copyfile(res["templates"].joinpath(file), semester.file_admin)
    logging.info(SuccessTouchd.format(name=name, file=file))
    
    file = semester.file_conda.name
    shutil.copyfile(res["templates"].joinpath(file.replace(name, "semester")),
                    semester.file_conda)
    logging.info(SuccessTouchd.format(name=name, file=file))
    sm_utils.write_conda(semester.file_conda)
    
    file = semester.file_slurm.name
    shutil.copyfile(res["templates"].joinpath(file), semester.file_slurm)
    logging.info(SuccessTouchd.format(name=name, file=file))
    sm_utils.write_conda(semester.file_slurm)


def make_notebooks(semester):
    validate_skeleton_presence(semester, prepnbs=True)
    
    Semester.coordinators = yaml.load(open(semester.file_admin, "r"))
    
    sm_utils.gen_notebook("make", **semester.gen_nb_args)


def validate_skeleton_presence(semester, prepnbs=False):
    files = [semester.file_sched, semester.file_admin]
    for file in files:
        existence = (not file.exists()) or (prepnbs and file.exists())
        if not existence:
            ErrFoundFile.format(name=semester.name, file=file.name)
    
    if not prepnbs:
        files = [semester.file_conda, semester.file_slurm]
        for file in files:
            if not file.exists():
                ErrFoundFile.format(name=semester.name, file=file.name)


def make_jekyll_posts(semester):
    Semester.coordinators = yaml.load(open(semester.file_admin, "r"))
    
    sm_utils.gen_jekyll_posts(**semester.gen_nb_args)


from string import Template
from admin import nb_utils
import requests
import imghdr
import imgkit
import datetime as dt
from admin import utils


def make_banners(semester):
    validate_skeleton_presence(semester, prepnbs=False)
    
    Semester.coordinators = yaml.load(open(semester.file_admin, "r"))

    banner = Template(open(utils.res_gen("semester", "templates", "event-banner.html"), "r").read())
    syllabus = yaml.load(open(semester.file_sched, "r"))

    banner_args = {
        "weekday": syllabus["week_day"],
        "time"   : syllabus["meet_time"],
        "room"   : syllabus["room"],
        "date"   : None,
        "title"  : None,
        "cover"  : None,
    }
    for unit in syllabus["teach"]:
        for meet in unit["list"]:
            nb_name = nb_utils.name(meet, semester.year)
            out = semester.workdir.joinpath(nb_name).joinpath("banner.jpg")
            
            # res = requests.get(meet["covr"], stream=True)
            # ext = imghdr.what(h=res.raw)
            # cov = semester.workdir.joinpath(nb_name).joinpath("cover." + ext)
            # with open(cov, "wb") as f:
            #     shutil.copyfileobj(res.raw, f)
        
            mm, dd = map(int, meet["date"].split("/"))
            banner_args["date"] = dt.date(semester.year, mm, dd).strftime("%b %d")
            banner_args["title"] = meet["name"]
            banner_args["cover"] = meet["covr"]
        
            banner_ = banner.substitute(banner_args)
            imgkit.from_string(banner_, out)


def update_notebooks(semester):
    validate_skeleton_presence(semester, prepnbs=True)
    
    Semester.coordinators = yaml.load(open(semester.file_admin, "r"))
    
    sm_utils.gen_notebook("update", **semester.gen_nb_args)
