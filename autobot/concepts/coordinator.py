from typing import Dict

# from autobot.apis.github import get_github_user


class Coordinator:
    def __init__(self, github: str, role: str) -> None:
        self.github = github.lower()
        assert self.github
        self.role = role

        self.name, self.web, self.bio = None, None, None
        # self._github_request()

    @staticmethod
    def parse_yaml(d: Dict) -> Dict:
        if "coordinators" in d:
            d = d["coordinators"]

        return {c["github"].lower(): Coordinator(**c) for c in d}

    # def _github_request(self) -> None:
    #     user = get_github_user(self.github)
    #     self.name = user.name
    #     self.website = user.blog
    #     self.bio = user.bio
    #     self.git_ln = user.url

    def as_metadata(self):
        return {"author": self.name, "github": self.github, "web": self.web}

    def as_md_heading(self):
        return f"{self.name} (@{self.github}[{self.git_ln}])"

    def __str__(self) -> str:
        return f"<Coordinator ({self.github}, {self.role})>"

    def __repr__(self) -> str:
        return self.github.lower()


# TODO add a Director class to avoid needing to specify things in a YAML
class Director(Coordinator):
    pass


# TODO add a President class to avoid needing to specify things in YAML
class President(Director):
    pass
