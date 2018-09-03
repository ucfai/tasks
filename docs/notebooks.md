## `notebook` submodule

Notebooks are the bread-and-butter of SIGAI. It's how we present the 
lecture-workshop hybrids; but you already knew this. :smiley:

Ultimately, this module doesn't need to be called directly. It's simply this
way to alleviate organizational nightmares and, effectively, assemble 
"namespaces."

Within `notebooks`, you should expect to find...
- `class Notebook` (in `__init__.py`)
- several NBConvert Jinja2 templates
- unit tests relevant to making sure you don't break anything. :winking_eye:
