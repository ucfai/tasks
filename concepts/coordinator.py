from typing import Dict


class Coordinator:
    def __init__(self, github: str) -> None:
        self.github = github.lower()

        # TODO implement attributes like this, could either pull from
        #      ucfai.org or their GitHub profile
        self.name, self.bio, self.web = None, None, None

    @staticmethod
    def parse_yaml(d: Dict) -> Dict:
        assert (
            "directors" in d and "coordinators" in d
        ), "Currently, we need both director and coordinator sections."

        ls = [] + d["directors"] + d["coordinators"]

        return {c.lower(): Coordinator(c) for c in ls}

    def as_metadata(self) -> Dict:
        return {"author": self.name, "github": self.github, "web": self.web}

    def as_md(self):
        return f"{self.name} ((@{self.github})[{self.git_url}])"

    def __str__(self):
        return self.github

    def __repr__(self):
        return f"<Coordinator ({self.github})>"


# TODO add a Director class to avoid specifying attributes in YAML
class Director(Coordinator):
    pass


# TODO add a President class to avoid specifying attributes in YAML
class President(Coordinator):
    pass
