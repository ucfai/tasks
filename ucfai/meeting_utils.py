import hashlib
import io
from pathlib import Path
from typing import Dict

import imgkit
import requests
from PIL import Image
import nbformat as nbf
from jinja2 import Template

from .meeting import Meeting


res_dir = Path(f"{__file__}").parent
tpl_banners = Template(open(res_dir/"html_tpl/event-banner.html").read())
tpl_heading = Template(open(res_dir/"html_tpl/nb-heading.html").read())

accepted_content_types = map(lambda x: f"image/{x}",
                             ["jpeg", "png", "gif", "tiff"])


def metadata(mtg: Meeting) -> Dict:
    return {
        "ucfai": {
            "authors": [c.to_metadata() for c in mtg.inst],
            "description": mtg.desc.strip(),
            "title": mtg.name,
            "date": mtg.meta.date.isoformat()[:10],  # outputs as 2018-01-16
        }
    }


def heading(mtg: Meeting, group: str) -> nbf.NotebookNode:
    tpl_args = {
        "group_sem": repr(group),
        "authors": mtg.inst,
        "title": mtg.name,
        "file": mtg.file,
        "date": mtg.meta.date.isoformat()[:10]
    }

    rendering = tpl_heading.render(**tpl_args)
    head_meta = {"name": mtg.name, "type": "sigai_heading"}
    return nbf.v4.new_markdown_cell(rendering, metadata=head_meta)


def create_and_save_banner(mtg: Meeting):
    out = None  # Semester.workdir(str(mtg), "banner.jpg")

    banner_arg = {
        "date": mtg.meta.date,
        "room": mtg.meta.room,
        "name": mtg.name.encode("ascii", "xmlcharrefreplace").decode("utf-8"),
    }

    ext = mtg.covr.split(".")[-1]
    cvr = requests.get(mtg.covr, headers={"user-agent": "Mozilla/5.0"})
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
    banner_ = tpl_banners.render(banner_arg)
    imgkit.from_string(banner_, out, options={"quiet": ""})
