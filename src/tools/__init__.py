from ..concepts import Meeting
from . import repositories, status, ucfcal, urls


def apply(fn, iterable, s: str = None):
    n_meets = len(iterable) - 1  # off-by-1s

    def _is_meeting(m):
        if type(m) in [tuple, list]:
            return next((x for x in m if isinstance(x, Meeting)), None)
        elif isinstance(m, Meeting):
            return m
        else:
            raise ValueError

    for idx, item in enumerate(iterable):
        m = _is_meeting(item)

        if s:
            print(f"({idx:2d}/{n_meets:2d}) {s}:", end=" ")

            if m:
                print(f"{str(m):40s} ...", end=" ")

        failmsg = fn(item)
        if s and not failmsg:  # successfully ran
            status.success(f"Successfull completed: {s}")
        elif failmsg:
            if m:
                failmsg += f" ~ {m.filename}"
            status.fail(failmsg)


__all__ = ["repositories", "ucfcal", "urls", "apply", "status"]
