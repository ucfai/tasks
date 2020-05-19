import emoji
import emojis


def _print(msg):
    fn = emoji.emojize
    # fn = emojis.encode
    print(fn(msg, use_aliases=True))


def success(s: str = ""):
    _print(f":white_check_mark: {s}")


def fail(s: str = ""):
    _print(f":x: {s}")


def warn(s: str = ""):
    _print(f":rotating_light: {s}")


def test(assertion, msg, halt: bool = True):
    try:
        assert assertion
    except AssertionError:
        fail(msg)
        if halt:
            exit(-1)
