res_dir = Path(__file__).parent.parent

def read(group: Group, meeting: Meeting):
    pass


def write(group: Group, meeting: Meeting):
    pass


def to_post(group: Group, meeting: Meeting):
    import nbconvert as nbc
    import nbformat as nbf

    md = nbc.MarkdownExporter()
    # changes to the template should, honestly, be done in the `tpl` file below
    #   this is largely to make sure we don't have a fragile class, but at a
    #   later date, there might be reason to extract it to a class - especially
    #   for readability purposes
    md.template_file = str(res_dir / "templates/notebooks/nb-as-post.tpl")

    nb = nbf.read(open(group.as_dir() / meeting.meta.sem / meeting.as_nb(), "r"))
    # need to copy the metadata as it doesn't get passed into the template to
    #   be extracted
    cp_metadata = nb["metdata"]["autobot"]

    body, resources = md.from_notebook_node(nb, resources={"metadata": cp_metadata})

    post_uri = group.as_dir() / meeting.as_post()

    with open(meeting.as_post(), "w") as f:
        f.write(body)

