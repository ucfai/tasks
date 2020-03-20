from typing import Union

long2short = {"fall": "fa", "summer": "su", "spring": "sp"}
# invert `long2short`
short2long = {k: v for v, k in long2short.items()}


class Semester:
    def __init__(self, name: str = "", year: Union[str, int] = "", shortname: str = ""):
        assert (name and year) or shortname  # TODO print out "help" text
        if name and year:
            shortname = long2short[name] + year[2:]
        else:
            name = short2long[shortname[:2]]
            year = "20" + shortname[2:]  # if this makes it into the next century, lol.

        self.name = name
        self.year = year
        self.shortname = shortname

    def __repr__(self):
        return self.shortname.lower()

    def __str__(self):
        return f"{self.name} {self.year}".capitalize()
