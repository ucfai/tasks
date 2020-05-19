from pathlib import Path
import textwrap
from typing import Dict

import pandas as pd
from ruamel.yaml.comments import CommentedSeq
from ruamel.yaml.representer import FoldedScalarString


def _inline_list(*ls):
    ls = CommentedSeq(*ls)
    ls.fa.set_flow_style()
    return ls


def _multiline_str(s, width=82):  # width=82 because 88-6 (6=indent level)
    return FoldedScalarString("".join(textwrap.wrap(s, width=width)))


class Meeting:
    def __init__(self, required: Dict, optional: Dict = {}):
        self.required = {}
        self.required["id"] = required["id"]
        self.required["date"] = str(required.get("date", ""))
        self.required["title"] = required["title"]
        self.required["authors"] = _inline_list(required.get("authors", []))
        self.required["filename"] = required["filename"]
        self.required["cover-image"] = required.get("cover-image", "")
        self.required["tags"] = _inline_list(required.get("tags", []))
        self.required["room"] = required.get("room", "")
        self.required["abstract"] = _multiline_str(required.get("abstract", ""))

        self.optional = {}

        self.optional["urls"] = optional.get("urls", None)
        if self.optional["urls"]:
            self.optional["urls"]["slides"] = optional["urls"].get("slides", "")
            self.optional["urls"]["youtube"] = optional["urls"].get("youtube", "")
        else:
            del self.optional["urls"]

        self.optional["kaggle"] = optional.get("kaggle", None)
        if self.optional["kaggle"] is True:
            pass
        elif self.optional["kaggle"]:
            if self.optional["kaggle"].get("kernels", False):
                self.optional["kaggle"]["kernels"] = _inline_list(
                    optional["kaggle"]["kernels"]
                )

            if self.optional["kaggle"].get("datasets", False):
                self.optional["kaggle"]["datasets"] = _inline_list(
                    optional["kaggle"]["datasets"]
                )

            if self.optional["kaggle"].get("enable_gpu", False):
                self.optional["kaggle"]["enable_gpu"] = optional["kaggle"]["enable_gpu"]

            if self.optional["kaggle"].get("competitions", False):
                self.optional["kaggle"]["competitions"] = _inline_list(
                    optional["kaggle"]["competitions"]
                )
        else:
            del self.optional["kaggle"]

        self.optional["papers"] = optional.get("papers", None)
        if not self.optional["papers"]:
            del self.optional["papers"]

    def __str__(self):
        return repr(self)

    def __repr__(self):
        try:
            assert self.flattened
        except (AttributeError, AssertionError):
            self.flatten()
        finally:
            s = self.filename

            if not pd.isnull(self.date):
                return f"{self.date.isoformat()[5:10]}-{s}"

            return s

    def flatten(self):
        if self.optional:
            self.__dict__.update(self.optional)

        if self.required:
            self.__dict__.update(self.required)

        self.date = pd.to_datetime(self.date)
        self.flattened = True

        return self

    def setup(self, parent: Path = Path(".")):
        path = parent / repr(self)
        path.mkdir()
        with open(path / ".metadata", "w") as f:
            f.write(self.id)
