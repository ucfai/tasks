from pathlib import Path
import logging

from . import sm_utils
from admin import res_semester as res

import shutil


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
            "nbs"    : self.notebooks,
            "year"   : self.year,
            "workdir": self.workdir,
            "sched"  : self.file_sched,
        }
    
    def make_skeleton(self):
        self.__validate_skeleton_presence()
        
        name = self.name
        
        file = self.file_sched.name
        shutil.copyfile(res["templates"].joinpath(self.file_sched.name),
                        self.file_sched)
        
        logging.info(SuccessTouchd.format(name=name, file=file))
        
        # Coordinators
        file = self.file_admin.name
        shutil.copyfile(res["templates"].joinpath(self.file_admin.name),
                        self.file_admin)
        
        logging.info(SuccessTouchd.format(name=name, file=file))
        
        # Conda
        file = self.file_conda.name
        conda_file = self.file_conda.name.replace(self.name, "semester")
        shutil.copyfile(res["templates"].joinpath(conda_file),
                        self.file_conda)
        
        logging.info(SuccessTouchd.format(name=name, file=file))
        sm_utils.write_conda(self.file_conda)
        
        # SLURM
        file = self.file_slurm.name
        shutil.copyfile(res["templates"].joinpath(self.file_slurm.name),
                        self.file_slurm)
        
        logging.info(SuccessTouchd.format(name=name, file=file))
        sm_utils.write_slurm(self.file_slurm)
        
    def make_notebooks(self):
        self.__validate_skeleton_presence(prepnbs=True)
        sm_utils.gen_notebook("make", **self.gen_nb_args)
    
    def __validate_skeleton_presence(self, prepnbs=False):
        name = self.name
        file = self.file_sched.name
        
        assert not self.file_sched.exists(), \
            ErrFoundFile.format(name=name, file=file)

        file = self.file_admin.name
        assert not self.file_admin.exists(), \
            ErrFoundFile.format(name=name, file=file)

        if not prepnbs:
            file = self.file_conda.name
            assert not self.file_conda.exists(), \
                ErrFoundFile.format(name=name, file=file)
    
            file = self.file_slurm.name
            assert not self.file_slurm.exists(), \
                ErrFoundFile.format(name=name, file=file)
    
    def make_jekyll_posts(self):
        
        pass

    def update_skeleton(self, file):
        self.__validate_skeleton_presence(prepnbs=True)
        sm_utils.gen_notebook("update", **self.gen_nb_args)
