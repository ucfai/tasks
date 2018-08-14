import datetime as dt


def name_notebook(entry, semyr):
    name = entry["file"]
    mm, dd = map(int, entry["date"].split("/"))
    
    tru_date = dt.date(int("20" + semyr), mm, dd)
    
    return tru_date, "-".join([str(tru_date), name])


import nbformat as nbf
from string import Template

modes = {
    "make"  : nbf.v4.new_notebook,
    "update": nbf.read,
}

nb_heading = Template("""# ${title}
----
by: ${authors}, on ${date}
""")


def gen_notebook(mode, syllabus, semester, admins):
    for unit in syllabus:
        for meet in unit["list"]:
            date, nb_name = name_notebook(meet, semester)
            nb_name += ".ipynb"
            
            nb_kwargs = {"fp": nb_name, "as_version": 4}
            # this is to make things a tad more readable
            nb_file = modes[mode](**nb_kwargs)
            
            nb_file["metadata"]["sigai"] = {
                "authors": [
                    {
                        "github": gh,
                        "name"  : admins[gh]["name"],
                    } for gh in meet["inst"]
                ],
                "title"  : meet["name"],
                "date"   : date.isoformat(),
                "unit"   : {
                    "name"  : unit["name"],
                    "number": unit["unit"]
                }
            }
            
            author_tuple = [
                (a["name"], a["github"])
                for a in nb_file["metadata"]["sigai"]["authors"]
            ]
            
            # NOTE: this is Markdown, ergo ()[] need to be escaped
            author_templ = Template("${name} \([@${gh}](github.com/${gh}/)\)")
            
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
            
            heading = nbf.v4.new_markdown_cell(curr_nb_heading,
                                               metadata=curr_nb_metadata)
            
            if mode == "new":
                nb_file["cells"].append(heading)
                
            elif mode == "update":
                heading_idx = next((idx
                                    for idx, cell in enumerate(nb_file["cells"])
                                    if cell["metadata"]["type"] is "sigai_heading"),
                                   None)
                nb_file["cells"][heading_idx] = heading
            
            with open(nb_name, "w") as _:
                nbf.write(nb_file, _)
