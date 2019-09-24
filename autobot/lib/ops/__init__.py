from .seed_semester import seed_semester

from .make_notebooks import make_notebooks
from .update_notebooks import update_notebooks
from .convert_notebooks import convert_notebooks

ACCEPTED = {
    "seed-semester": seed_semester,
    "make-notebooks": make_notebooks,
    "update-notebooks": update_notebooks,
    "convert-notebooks": convert_notebooks,
}
