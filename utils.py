from pathlib import Path

res_semester  = ["templates"]
res_arcc      = ["templates"]
res_notebooks = ["templates"]

res_semester  = {k: f"{k}/semester/" for k in res_semester}
res_arcc      = {k: f"{k}/arcc/" for k in res_arcc}
res_notebooks = {k: f"{k}/notebooks/" for k in res_notebooks}

res_semester  = {k: Path(f"admin/{v}") for k, v in res_semester.items()}
res_arcc      = {k: Path(f"admin/{v}") for k, v in res_arcc.items()}
res_notebooks = {k: Path(f"admin/{v}") for k, v in res_notebooks.items()}

resources = {
    "semester" : res_semester,
    "arcc"     : res_arcc,
    "notebooks": res_notebooks,
}


def res_gen(key, loc, pth):
    return resources[key][loc].joinpath(pth)
