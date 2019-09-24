from pathlib import Path
import os

from autobot.meta import Group


def force_root():
    # safety.py \ lib \ autobot \ <autobot-root> \ <jenkins-root>
    path = Path(__file__).parent.parent.parent.parent

    os.chdir(path)
