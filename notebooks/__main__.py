from argparse import ArgumentParser

import logging
import pathlib

import yaml

from . import utils


class Notebook:
    def __init__(self, semester, op):
        self.sem_name = semester
        self.sem_path = pathlib.Path(self.sem_name)
        # ensure the directory exists
        self.sem_path.mkdir(exist_ok=True)
        
        # ensure the syllabus exists
        self.syllabus_file = self.sem_path.joinpath("syllabus.yml")
        assert self.syllabus_file.exists(), \
            "Failed to find the `syllabus` for {}".format(self.sem_name)
        self.syllabus_read = yaml.load(open(self.syllabus_file, "r"))
        
        self.sem_admins_file = self.sem_path.joinpath("coordinators.yml")
        assert self.sem_admins_file.exists(), \
            "Failed to find the `coordinators` for {}".format(self.sem_name)
        self.sem_admins_read = yaml.load(open(self.sem_admins_file, "r"))
        
        self.gen_nb_kwargs = {
            "syllabus": self.syllabus_read,
            "semester": self.sem_name,
            "admins"  : self.sem_admins_read
        }
        
        eval("self.__" + op)()
    
    def __make(self):
        utils.gen_notebook("make", **self.gen_nb_kwargs)
    
    def __update(self):
        utils.gen_notebook("update", **self.gen_nb_kwargs)
        
    def __convert(self):
        pass


if __name__ == "__main__":
    parser = ArgumentParser(
            description="Generates the template-ized Jupyter Notebooks we used "
                        "for every lecture and adds in metadata to be used "
                        "when converting given Notebooks into corresponding "
                        "HTML to be posted on the web.")
    
    parser.add_argument("semester", help="Chosen semester to create/modify.")
    
    parser.add_argument("op", choices=["make", "update", "convert"])
    
    args = parser.parse_args()

    logging.basicConfig(format="%(levelname)10s | %(message)s",
                        filename="logs/notebooks.log", level=logging.DEBUG)

    nb = Notebook(args.semester, args.op)
