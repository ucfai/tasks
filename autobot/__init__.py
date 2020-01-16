from pathlib import Path
from typing import Union
import os

ORG_NAME = "ucfai"


def get_template(s: Union[str, Path], as_str: bool = False):
    path = Path(__file__).parent / "templates" / s
    return path if not as_str else str(path)


def get_setup_template(s: Union[str, Path], as_str: bool = False):
    return get_template(Path("setup") / s, as_str=as_str)


def get_upkeep_template(s: Union[str, Path], as_str: bool = False):
    return get_template(Path("upkeep") / s, as_str=as_str)


def load_template(s: Union[str, Path]):
    return Template(open(get_template(s), "r").read())


def load_setup_template(s: Union[str, Path]):
    return Template(open(get_setup_template(s), "r").read())


def load_upkeep_template(s: Union[str, Path]):
    return Template(open(get_upkeep_template(s), "r").read())


# if "IN_DOCKER" in os.environ:
#     os.chdir("/")
# else:
#     exit("`autobot` should be run in a Docker container moving forward.")
