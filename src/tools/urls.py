import re

import requests

from .. import Meeting
from . import repositories


def youtube(m: Meeting):
    # YouTube URLs take the following form:
    #   https://www.youtube.com/watch?v=dQw4w9WgXcQ
    #   https://youtu.be/dQw4w9WgXcQ

    try:
        url = m.urls["youtube"]
    except (KeyError, AttributeError):
        return ""

    #   YouTube IDs are likely to stay 11-characters, but we'll see:
    #   https://stackoverflow.com/a/6250619
    if len(url) > 11 and "youtu" in url:
        # remove the protocol, www, and YouTube's domain name
        proto = "(?:https?://)?"
        ln_old = "(?:www\.)?youtube.com/watch?v="
        ln_new = "youtu.be"
        yt_full = f"{proto}(?:{ln_old}|{ln_new})"

        # "...|$" returns the empty string if not a match
        url = re.sub(f"{yt_full}|$", "", url)
        url = re.search("([A-Za-z0-9-_]{11})", url).group(0)
        url = f"https://youtu.be/{url}"
        if requests.get(url).status_code == requests.codes.OK:
            return url

    return ""


def slides(m: Meeting):
    # Google Slides URLs take the following form:
    #   https://docs.google.com/presentation/d/14uUXIrdmXMGChj4dYaCZxcQ-rFonLmKqlSppLu8cY_I

    try:
        url = m.urls["slides"]
    except (KeyError, AttributeError):
        return ""

    if "docs" in url and "presentation" in url:
        # remove the protocol, www, and YouTube's domain name
        docs_base_url = "(?:https?://)?docs.google.com/presentation/d/"

        # "...|$" returns the empty string if not a match
        url = re.sub(f"{docs_base_url}|$", "", url)
        url = url.split("/", maxsplit=1)[0]
        url = f"https://docs.google.com/presentation/d/{url}"
        if requests.get(url).status_code == requests.codes.OK:
            return url

    # TODO based on how using `slides` in Hugo Academic works out, update this

    return ""


def github(m: Meeting):
    # Our GitHub URLs take the form:
    #   https://github.com/ucfai/<meeting.group>/blob/master/<meeting.group.semester>/<meeting>
    #   e.g. https://github.com/ucfai/core/fa19/blob/master/2019-09-18-regression

    url = f"{repositories.remote_meeting_root(m)}/{m.filename}.ipynb"
    return url if requests.get(url).status_code == requests.codes.OK else ""


def kaggle(m: Meeting):
    from ..apis.kaggle import slug_kernel, _username

    url = f"https://kaggle.com/{_username}/{slug_kernel(m)}"
    return url if requests.get(url).status_code == requests.codes.OK else ""


def colab(m: Meeting):
    url = f"{repositories.remote_meeting_root(m)}/{m.filename}.ipynb"

    if requests.get(url).status_code == requests.codes.OK:
        return url.replace(
            repositories.REMOTE_CONTENT_PLATFORM,
            "https://colab.research.google.com/github",
        )
    else:
        return ""
