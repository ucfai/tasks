from github.GithubException import GithubException
from github.MainClass import Github
from github.NamedUser import NamedUser as User
from github.Organization import Organization as Org
from github.Team import Team

from autobot import ORG_NAME
from autobot.concepts import Group

# GH_API_KEY = os.environ["GITHUB_API_KEY"]
_GH_API_KEY = "ca9c8efd282ec1bc79dd10e9a84d2883f0104a51"

_api: Github = Github(_GH_API_KEY, api_preview=True)
_org: Org = _api.get_organization(ORG_NAME)
_team: Team = None
_coord_team: Team = None

_gen_err = "There's something wrong surrounding the GitHub API."


# region Actual calls to the GitHub API
def get_github_user(user: str) -> User:
    return _api.get_user(user)


def create_semester_team(grp: Group) -> int:
    # TODO: Enable nested teams (waiting on PyGitHub to implement this)
    global _team
    _team = _org.create_team(grp.sem.short, privacy="public")
    return _team.id


def add_coordinators(grp: Group) -> None:
    # TODO: ensure `coord_team` is set to allow for adding/retrieving subteams
    global _team
    if not _team:
        try:
            create_semester_team(grp)
        except GithubException:
            teams = _org.get_teams()
            t: Team = None
            for t in teams:
                if t.name == grp.sem.short:
                    break
            _team = _org.get_team(t.id)

    roles = lambda x: "maintainer" if x in ["Director"] else "member"

    for coord in grp.coords.items():
        _team.add_membership(coord.github, role=roles(coord.role))


# endregion
