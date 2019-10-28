from pathlib import Path
from typing import Union

ORG_NAME = "ucfai"


def get_template(s: Union[str, Path], as_str: bool = False):
    path = Path(__file__).parent / "templates" / s
    return path if not as_str else str(path)
