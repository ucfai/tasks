from hashlib import sha256
import io
import warnings

from jinja2 import Template
from PIL import Image
import requests
import imgkit

from autobot import get_template
from autobot.meta import Meeting

def render_cover(meeting: Meeting):
    """Generates the banner images for each meeting. These should be posted
       to the website as well as relevant social media.

    NOTE: This function is destructive. It will overwrite the banner it's
    generating - this is intentional behavior, ergo **do not edit banners
    directly**.
    """
    template_banner = Template(open(get_template("event-banner.html"), "r").read())

    accepted_content_types = [
        f"image/{x}" for x in ["jpg", "jpeg", "png", "gif", "tiff"]
    ]

    extension = meeting.required["cover"].split(".")[-1]

    cover_image_path = paths.site_post_assets(meeting) / "cover.png"

    # snag the image from the URL provided in the syllabus
    cover = requests.get(
        meeting.required["cover"], headers={"user-agent": "Mozilla/5.0"}
    )
    # use this to mute the EXIF data error ~ this seems to be a non-issue based
    #   on what I've read (@ionlights) ~ circa Sep/Oct 2019
    warnings.filterwarnings("ignore", "(Possibly )?corrupt EXIF data", UserWarning)
    if cover.headers["Content-Type"] in accepted_content_types:
        image_as_bytes = io.BytesIO(cover.content)
        try:
            # noinspection PyTypeChecker
            cover_as_bytes = io.BytesIO(open(cover_image_path, "rb").read())

            # get hashes to check for diff
            image_hash = sha256(image_as_bytes.read()).hexdigest()
            cover_hash = sha256(cover_as_bytes.read()).hexdigest()

            # clearly, something has changed between what we have and what
            #   was just downloaded -> update
            if cover_hash != image_hash:
                image = Image.open(image_as_bytes)
            else:
                image = Image.open(cover_as_bytes)
        except FileNotFoundError:
            image = Image.open(image_as_bytes)
        finally:
            image.save(cover_image_path)

    out = cover_image_path.with_name("banner.png")

    banner = template_banner.render(meeting=meeting, cover=cover_image_path.absolute())

    imgkit.from_string(
        banner,
        out,
        options={
            # standard flags should be passed as dict keys with empty values...
            "quiet": "",
            "debug-javascript": "",
            "enable-javascript": "",
            "javascript-delay": "400",
            "no-stop-slow-scripts": "",
        },
    )

def render_weekly_instagram_post(meeting: Meeting):
    raise NotImplementedError()

def render_video_background(meeting):
    raise NotImplementedError()