from jinja2 import Template

from admin import notebooks


def gen_notebook(mode, sched, year, workdir, nbs):
    for unit in sched:
        for meet in unit["list"]:
            nb_name = notebooks.nb_utils.name(meet, year)
            if mode is "make":
                workdir.joinpath(nb_name).mkdir()

            nbs[nb_name] = notebooks.N(nb_name, unit, meet)
            eval("self.notebooks[nb_name]._" + mode)()
            notebooks.nb_utils.write(nbs[nb_name])


def write_slurm(self):
    with open("templates/jupyter_notebooks.slurm", "r") as f:
        tpl_slurm = Template(f.read())
    
    tpl_slurm_args = {}
    
    with open(self.file_slurm, "w") as f:
        f.write(tpl_slurm.render(**tpl_slurm_args))


def write_conda(self):
    with open("templates/jupyter_notebooks.slurm", "r") as f:
        tpl_slurm = Template(f.read())
    
    tpl_slurm_args = {}
    
    with open(self.file_slurm, "w") as f:
        f.write(tpl_slurm.render(**tpl_slurm_args))
