from pathlib import Path
from typing import Union

from jinja2 import Template

_HERE = Path(__file__)
_ROOT = _HERE.parent.parent


def get(s: Union[str, Path], as_str: bool = False):
    path = _ROOT / "templates" / s
    return path if not as_str else str(path)


def get_setup(s: Union[str, Path], as_str: bool = False):
    return get(Path("setup") / s, as_str=as_str)


def get_upkeep(s: Union[str, Path], as_str: bool = False):
    return get(Path("upkeep") / s, as_str=as_str)


def load(s: Union[str, Path]):
    return Template(open(get(s), "r").read())


def load_setup(s: Union[str, Path]):
    return Template(open(get_setup(s), "r").read())


def load_upkeep(s: Union[str, Path]):
    return Template(open(get_upkeep(s), "r").read())
