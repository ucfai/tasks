from pathlib import Path
import logging

from . import sm_utils

from string import Template
import shutil

ErrFoundFile = Template("Found `${name}/${file}`. Let's not continue, "
                        "to avoid overriding.")
ErrNotFoundFile = Template("Couldn't find `${name}/${file}.${ext}`. Please "
                           "restart from `make` command - NOTE this overwrites"
                           "any changes you may have made.")

SuccessTouchd = Template("Successfully touch'd `${name}/${file}.${ext}`.")


class Semester:
    coordinators = None
    
    def __init__(self, name_, topic_, cwd):
        self.year = int("20" + name_[-2:])
        self.name = name_
        self.topic = topic_
        
        self.workdir = Path(cwd).joinpath(self.topic).joinpath(self.name)
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
            "nbs"    : self.notebooks,
            "year"   : self.year,
            "workdir": self.workdir,
            "sched"  : None
        }
    
    def _make(self):
        subs_ = {
            "name": self.name,
            "file": self.file_sched.name,
        }
        
        # Syllabus
        assert not self.file_sched.exists(), ErrFoundFile.substitute(subs_)
        shutil.copyfile("templates/" + self.file_sched.name, self.file_sched)
        logging.info(SuccessTouchd.substitute(subs_))
        
        # Coordinators
        subs_["file"] = self.file_admin.name
        assert not self.file_admin.exists(), ErrFoundFile.substitute(subs_)
        shutil.copyfile("templates/" + self.file_admin.name, self.file_admin)
        logging.info(SuccessTouchd.substitute(subs_))
        
        # Conda
        subs_["file"] = self.file_conda.name
        assert not self.file_conda.exists(), ErrFoundFile.substitute(subs_)
        shutil.copyfile("templates/" + self.file_conda.name, self.file_conda)
        logging.info(SuccessTouchd.substitute(subs_))
        sm_utils.write_conda()
        
        # SLURM
        subs_["file"] = self.file_slurm.name
        assert not self.file_slurm.exists(), ErrFoundFile.substitute(subs_)
        shutil.copyfile("templates/" + self.file_slurm.name, self.file_slurm)
        logging.info(SuccessTouchd.substitute(subs_))
        sm_utils.write_slurm()
        
        input("Waiting for you to edit `{}/{{syllabus, coordinators}}."
              "yml. (Press `Enter` once done.) [You can always come back "
              "later, just be sure to run `update` instead!)".format(self.name))
        
        sm_utils.gen_notebook("make", **self.gen_nb_args)
    
    def _update(self):
        subs_ = {
            "name": self.name,
            "file": "syllabus",
            "ext" : "yml"
        }
        
        assert self.file_sched.exists(), ErrNotFoundFile.substitute(subs_)
        
        subs_["file"] = "coordinators"
        assert self.file_admin.exists(), ErrNotFoundFile.substitute(subs_)
        
        subs_["file"] = self.name + ".env"
        assert self.file_conda.exists(), ErrNotFoundFile.substitute(subs_)
        
        subs_["file"] = self.name
        subs_["ext"] = "slurm"
        assert self.file_slurm.exists(), ErrNotFoundFile.substitute(subs_)
        
        sm_utils.gen_notebook("update")
    
    def _jekyll(self):
        pass
