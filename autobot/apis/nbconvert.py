from typing import Tuple
import json

import nbformat
from nbconvert.exporters import MarkdownExporter, NotebookExporter
from nbconvert.exporters.exporter import ResourcesDict
from nbconvert.preprocessors import (
    Preprocessor,
    TagRemovePreprocessor,
)
from nbconvert.writers import FilesWriter
from nbformat import NotebookNode
from nbgrader.preprocessors import ClearOutput, ClearSolutions

from autobot.actions import paths
from autobot.concepts import Meeting
from autobot.pathing import templates, urlgen


class FileExtensions:
    Solutionbook = ".solution.ipynb"
    Workbook = ".ipynb"

    def __init__(self):
        raise NotImplementedError("This equivalent to an Enum.")


def read_notebook(meeting: Meeting, suffix: str = FileExtensions.Solutionbook):
    notebook_path = paths.repo_meeting_folder(meeting) / repr(meeting)
    if not notebook_path.with_suffix(suffix).exists():
        return nbformat.v4.new_notebook()
    else:
        return nbformat.read(str(notebook_path.with_suffix(suffix)), as_version=4)


class SolutionbookToPostExporter(MarkdownExporter):
    """AI@UCF Custom Notebook Exporter; this produces both the website and non-solution
    entries.
    """

    def __init__(self, config=None, **kwargs):
        self.template_path = [str(templates.get_upkeep("meetings"))]
        self.template_file = "to-post.md"
        self.template_extension = ".j2"

        # This removes the `In [X]:` snippets of the notebook
        #   **but not the actual code snippets!**
        self.exclude_input_prompt = True
        # from: https://github.com/jupyter/nbconvert/blob/b31a5af48ee159f579c021b897727374f28a0800/nbconvert/exporters/templateexporter.py#L237

        # This removes the `Out [X]:` snippets of the notebook
        #   **but not the actual code output!**
        self.exclude_output_prompt = True
        # from: https://github.com/jupyter/nbconvert/blob/b31a5af48ee159f579c021b897727374f28a0800/nbconvert/exporters/templateexporter.py#L245

        self.no_prompt = True

        # This removes the title cell that's placed at the beginning of every notebook.
        self.register_preprocessor(
            TagRemovePreprocessor(remove_cell_tags=["nb-title"]), enabled=True
        )

        # NOTE this is only needed if exporting code segments to HTML
        # This adds the `Highlight2HTML` pygment lexer to the filters so it's available
        #   to the template, since we want Markdown output **except** for code cells.
        # This is so we can use proper `pygments` styling (this allows us to mimic IDE
        #   coloring) and raw "```python ...```" markdown isn't supported by
        #   `highlight.js`.
        # mimic'd from: https://github.com/jupyter/nbconvert/blob/b31a5af48ee159f579c021b897727374f28a0800/nbconvert/exporters/html.py#L99
        # from nbconvert.filters.highlight import Highlight2HTML
        # self.register_filter("highlight_code", Highlight2HTML(parent=self))

    def from_meeting(self, meeting: Meeting):
        notebook_path = paths.repo_meeting_folder(meeting) / "".join(
            [repr(meeting), FileExtensions.Solutionbook]
        )

        # TODO concatenate front matter to notebook output
        front_matter = templates.load_upkeep("meetings/hugo-front-matter.md.j2")
        front_matter = front_matter.render(
            **{
                "group": repr(meeting.group),
                "meeting": {
                    "title": meeting.required["title"],
                    "date": meeting.meta.date.isoformat(),
                    # TODO decide on what date qualifies to be `lastmod`
                    "lastmod": meeting.meta.date.isoformat(),
                    "authors": meeting.required["instructors"],
                    "tags": meeting.optional["tags"],
                    "description": meeting.required["description"],
                    "weight": meeting.number,
                },
                "semester": {
                    "full": str(meeting.group.semester),
                    "short": repr(meeting.group.semester),
                },
                "urls": {
                    "youtube": urlgen.youtube(meeting),
                    "slides": urlgen.slides(meeting),
                    "github": urlgen.github(meeting),
                    "kaggle": urlgen.kaggle(meeting),
                    "colab": urlgen.colab(meeting),
                },
            }
        )

        # the notebook is output as a string, so treat it as such when concatenating
        notebook, resources = self.from_filename(str(notebook_path), resources=None)
        resources.update({"output_extension": ".md"})

        writer = FilesWriter(
            build_directory=str(paths.site_group_folder_from_meeting(meeting))
        )

        front_matter_plus_notebook = f"{front_matter}\n{notebook}"

        writer.write(
            front_matter_plus_notebook, resources, meeting.required["filename"]
        )
        # writer.write(notebook, resources, meeting.required["filename"])

        return notebook, resources


class SolutionbookToWorkbookExporter(NotebookExporter):
    def __init__(self, config=None, **kwargs):
        super(NotebookExporter, self).__init__(
            config,
            preprocessors=[ValidateNBGrader, CustomClearSolutions, ClearOutput],
            **kwargs,
        )

    def from_meeting(self, meeting: Meeting):
        nb = read_notebook(meeting)

        resources = {"output_extension": FileExtensions.Workbook}
        notebook, resources = super().from_notebook_node(nb, resources)

        writer = FilesWriter(build_directory=str(paths.repo_meeting_folder(meeting)))
        writer.write(json.dumps(notebook), resources, repr(meeting))

        return notebook, resources


class TemplateNotebookValidator(NotebookExporter):
    def __init__(self, config=None, **kwargs):
        super(TemplateNotebookValidator, self).__init__(config, **kwargs)

        self.register_preprocessor(
            TagRemovePreprocessor(remove_cell_tags=["nb-title"]), enabled=True
        )
        self.register_preprocessor(ValidateNBGrader(), enabled=True)

    def from_meeting(self, meeting: Meeting):
        self.meeting = meeting

        nb = read_notebook(meeting)

        resources = {"output_extension": FileExtensions.Solutionbook}
        notebook, resources = super(NotebookExporter, self).from_notebook_node(
            nb, resources=resources
        )

        notebook.cells.insert(0, self._notebook_heading())

        writer = FilesWriter(build_directory=str(paths.repo_meeting_folder(meeting)))

        writer.write(json.dumps(notebook), resources, repr(meeting))

        return notebook, resources

    def _notebook_heading(self) -> nbformat.NotebookNode:
        tpl_heading = templates.load_upkeep("meetings/notebook-heading.html.j2")

        tpl_args = {
            "group_sem": paths.repo_meeting_folder(self.meeting),
            "authors": [
                self.meeting.group.coords[author]
                for author in self.meeting.required["instructors"]
            ],
            "title": self.meeting.required["title"],
            "file": self.meeting.required["filename"],
            "date": self.meeting.meta.date.isoformat()[:10],
        }

        rendering = tpl_heading.render(**tpl_args)
        head_meta = {"title": self.meeting.required["title"], "tags": ["nb-title"]}

        return nbformat.v4.new_markdown_cell(rendering, metadata=head_meta)

    def _notebook_metadata(self) -> dict:
        return {
            "autobot": {
                "authors": [
                    self.meeting.group.coords[c.lower()].as_metadata()
                    for c in self.meeting.required["instructors"]
                ],
                "description": self.meeting.required["description"].strip(),
                "title": self.meeting.required["title"],
                "date": self.meeting.meta.date.isoformat()[:10],
                "tags": self.meeting.optional["tags"],
                "categories": [self.meeting.group.semester.short],
            }
        }


class CustomClearSolutions(ClearSolutions):
    ENFORCE_METADATA = False
    BEGIN_SOLUTION_FLAG = "BEGIN SOLUTION"
    END_SOLUTION_FLAG = "END SOLUTION"

    def __init__(self, config=None, **kwargs):
        super(ClearSolutions, self).__init__(**kwargs)
        self.enabled = True

        self.enforce_metadata = self.ENFORCE_METADATA
        self.begin_solution_delimeter = self.BEGIN_SOLUTION_FLAG
        self.end_solution_delimeter = self.END_SOLUTION_FLAG


class ValidateNBGrader(Preprocessor):
    def preprocess_cell(
        self, cell: NotebookNode, resources: ResourcesDict, cell_index: int
    ) -> Tuple[NotebookNode, ResourcesDict]:
        if cell.cell_type != "code":
            return cell, resources

        nbgrader_cell_metadata = {"nbgrader": {"solution": True}}

        source = "".join(cell.source).lower()
        if (
            CustomClearSolutions.BEGIN_SOLUTION_FLAG.lower() in source
            and CustomClearSolutions.END_SOLUTION_FLAG.lower() in source
        ):
            cell.metadata.update(nbgrader_cell_metadata)
        elif "nbgrader" in cell.metadata:
            del cell.metadata["nbgrader"]

        return cell, resources
