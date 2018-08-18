"""This module generates the template-ized Jupyter Notebooks we used for every
lecture and adds in metadata to be used when converting given Notebooks into
corresponding HTML to be posted on the web.
"""

__all__ = ["nb_utils", "notebooks"]

__author__ = "John Muchovej <j+sigai@ionlights.org>"
__maintainer__ = "SIGAI@UCF, <admins@ucfsigai.org>"
__version__ = "0.1"


from .notebooks import Notebook as N
from . import nb_utils
