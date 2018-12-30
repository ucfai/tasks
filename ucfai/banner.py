import io
import hashlib
from pathlib import Path

import requests
from PIL import Image
from jinja2 import Template
import imgkit

from .mtg import Meeting

res_dir = Path(f"{__file__}").parent
banner_tpl = Template(open(res_dir/"html_tpl/event-banner.html").read())

accepted_content_types = map(lambda x: f"image/{x}",
                             ["jpeg", "png", "gif", "tiff"])


class Banner:
    def __init__(self, url: str):
        self.url = url

    def create_and_save(self, mtg: Meeting):
        from .mtg import Meeting
        assert type(mtg) == Meeting
        out = None  # Semester.workdir(str(mtg), "banner.jpg")

        banner_arg = {
            "date": mtg.meta.date,
            "room": mtg.meta.room,
            "name": mtg.name.encode("ascii", "xmlcharrefreplace").decode("utf-8"),
        }

        ext = mtg.covr.split(".")[-1]
        cvr = requests.get(self.url, headers={"user-agent": "Mozilla/5.0"})
        cvr_pth = "None"  # Semester.workdir(str(mtg), "cover." + ext)
        if cvr.headers["Content-Type"] in accepted_content_types:
            img_bytes = io.BytesIO(cvr.content)
            try:
                cvr_bytes = io.BytesIO(open(cvr_pth).read())
                cvr_hash = hashlib.sha256(cvr_bytes).hexdigest()
                img_hash = hashlib.sha256(img_bytes).hexdigest()
                diff = (cvr_hash != img_hash)
                if diff:
                    img = Image.open(img_bytes)
                    img.save(cvr_pth)
            except FileNotFoundError:
                pass

        banner_arg["cover"] = cvr_pth
        banner_ = banner_tpl.render(banner_arg)
        imgkit.from_string(banner_, out, options={"quiet": ""})
