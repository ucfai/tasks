import os
from typing import Dict

import requests
import github
from github.NamedUser import NamedUser as User
from github.Organization import Organization as Org
from github.Team import Team
from github.MainClass import Github
from github.GithubException import GithubException

from ucfai.meta.group import Group

GH_API_KEY = os.environ["GITHUB_API_KEY"]
GH_API_KEY = "537f106b2160cc3de901d26d56dc731b87680284"

api: Github = Github(GH_API_KEY, api_preview=True)
org: Org = api.get_organization("ucfai")
team: Team = None
coord_team: Team = None

_gen_err = "There's something wrong surrounding the GitHub API."


# region Actual calls to the GitHub API
def get_github_user(user: str) -> User:
    return api.get_user(user)


def create_semester_team(grp: Group) -> int:
    # TODO: Enable nested teams (waiting on PyGitHub to implement this)
    global team
    team = org.create_team(grp.sem.short, privacy="public")
    return team.id


def add_coordinators(grp: Group) -> None:
    # TODO: ensure `coord_team` is set to allow for adding/retrieving subteams
    global team
    if not team:
        try:
            create_semester_team(grp)
        except GithubException:
            teams = org.get_teams()
            t: Team = None
            for t in teams:
                if t.name == grp.sem.short:
                    break
            team = org.get_team(t.id)

    roles = lambda x: "maintainer" if x in ["Director"] else "member"

    for coord in grp.coords.items():
        team.add_membership(coord.github, role=roles(coord.role))
# endregion
