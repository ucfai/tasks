import requests

github_api_url = "https://api.github.com"


class Coordinator:
    def __init__(self, github: str, role: str) -> None:
        self.github = github
        assert self.github
        self.role = role

        self.name, self.web, self.bio = None, None, None
        self._github_request()

    def _github_request(self) -> None:
        # https://developer.github.com/v3/users/#response-with-public-profile-information
        user_req_url = f"{github_api_url}/users/{self.github}"
        resp = requests.get(user_req_url)
        if resp.status_code != requests.codes.ok:
            raise ValueError(
                f"Failed to get profile info of {self.github}; " +
                "there's something wrong surrounding the GitHub API.")
        json = resp.json()
        self.name = json["name"]
        self.website = json["blog"]
        self.bio = json["bio"]

    def to_metadata(self):
        return {
            "author": self.name,
            "github": self.github,
            "web"   : self.web,
        }

    def to_md_heading(self):
        git_ln = f"https://github.com/{self.github}"
        return f"{self.name} (@{self.github}[{git_ln}])"

    def __str__(self) -> str:
        return f"<Coordinator ({self.github}, {self.role})>"
