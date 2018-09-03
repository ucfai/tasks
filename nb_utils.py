import nbformat as nbf

from string import Template

from admin import semester

nb_heading = Template("""# ${title}
---
by: ${authors}, on ${date}
""")
author_templ = Template("${name} \([@${gh}](github.com/${gh}/)\)")


def heading(nb, date, meet):
    author_tuple = [
        (a["name"], a["github"])
        for a in nb["metadata"]["sigai"]["authors"]
    ]
    
    curr_nb_heading = nb_heading.safe_substitute({
        "title"  : meet["name"],
        "authors": ", ".join(
                [author_templ.safe_substitute({
                    "name": name,
                    "gh"  : gh,
                }) for name, gh in author_tuple]),
        "date"   : date.strftime("%m %b %Y"),
    })
    
    curr_nb_metadata = {
        "name": meet["name"],
        "type": "sigai_heading"
    }
    
    return nbf.v4.new_markdown_cell(curr_nb_heading,
                                    metadata=curr_nb_metadata)


def metadata(date, meet, unit):
    return {
        "sigai": {
            "authors"    : [
                {
                    "github": gh,
                    "name"  : semester.Semester.coordinators[gh]["nam"],
                } for gh in meet["inst"]
            ],
            "description": meet["desc"].strip(),
            "title"      : meet["name"],
            "date"       : date.isoformat(),
            "unit"       : {
                "name"  : unit["name"],
                "number": unit["unit"]
            }
        }
    }


import datetime as dt


def name(entry, year):
    mm, dd = map(int, entry["date"].split("/"))
    
    return "-".join([str(dt.date(year, mm, dd)), entry["file"]])


def write(nb):
    with open(nb.name, "w") as _:
        nbf.write(nb.nb, _)
