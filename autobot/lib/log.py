def debug(s: str):
    pass

def warning(s: str, prompt: bool = False):
    print(s)
    if prompt:
        return input("Continue? [y/N] ").lower() in ["y", "yes"]

def info(s: str):
    pass
