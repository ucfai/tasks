import os
import re
import signal
import sys
from datetime import datetime
from getpass import getpass
from pathlib import Path
from time import sleep

import pandas as pd
import requests

from termcolor import colored, cprint

__author__ = "John Muchovej"


BASEURL = "https://auth.ucfai.org/"
BASEURL = "http://localhost:3000/"
API_URL = "api/v1/pids"

READERS = "HID c216:0180"  # card reader IDs

# TODO: Get on UCF WiFi
# Attempt to get on to UCF Guest without using WebUI via:
# POST http://192.0.2.1/login.html
# TODO: Setup `evdev`
# TODO: Setup local logging if API fails
# TODO: Local logging backup to either GCP or the DB


class Person:
    def __init__(self, pid: str, givenname: str, surname: str, iso: str):
        assert len(pid) == 7, pid
        assert len(iso) == 16, iso

        self._pid = int(pid)
        self._iso = int(iso)
        self._givenname = givenname.strip()
        self._surname = surname.strip()

        self._english_name = f"{self._givenname} {self._surname}"
        self._first_name_guess = self._givenname.split(" ")[0]
        pass

    def __str__(self):
        return f"Hi, {self._first_name_guess.capitalize()}"

    def submit(self):
        return {
            "pid": self._pid,
            "iso": self._iso,
            "givenname": self._givenname,
            "surname": self._surname,
            "stamp": datetime.now(),
        }


class UCFID:
    def __init__(self):
        pass

    def connect(self):
        pass

    def listen(self):
        while True:
            try:
                info = getpass(prompt="Swipe your UCF ID card")
                person = self._parse(info)
                success = self._send(person)
                cprint(str(person), "green", attrs=["bold"])
                sleep(1.5)
                os.system("clear")
            except KeyboardInterrupt:
                return
            except:
                cprint("Failed to add! Reswipe.", "red", attrs=["bold", "blink"])

    def _send(self, person: Person) -> bool:
        payload = {}
        # payload["auth_token"] = os.environ["AUTH_TOKEN"]
        payload.update(person.submit())

        # TODO implement submission to some database that we maintain
        # resp = requests.post(BASEURL + API_URL, json=payload)
        pid_dicts.append(payload)

        return True

        # return resp.status_code == requests.codes.ok

    def _parse(self, tracks12: str) -> Person:
        track1, track2 = tracks12.split(";", maxsplit=2)

        track1_regex = re.compile("%B(.+)\^(.+)\^(.+)?")
        track1_extract = track1_regex.match(track1).groups()
        iso, name, pid = track1_extract

        surname, givenname = name.split("/")
        pid = re.compile(".*000000(\d{7}).*").match(pid).groups()[0]

        # NOTE: We don't need anything from Track 2
        # track2_regex = re.compile()
        # track2_extract = track2_regex.match(track2)

        return Person(pid, givenname, surname, iso)


def save():
    df = pd.DataFrame(pid_dicts)
    df = df.drop_duplicates(subset=["pid"])
    df = df.set_index(["stamp", "pid"])
    df.to_csv(f"pids-{datetime.today().date()}.csv", index=True, mode="w")
    df.to_pickle(f"pids-{datetime.today().date()}.pkl")


def _sigterm(_signo, _stack_frame):
    save()
    exit(0)


if __name__ == "__main__":
    me = Path(__file__)
    if "IN_DOCKER" not in os.environ and "site-packages" not in str(me):
        print(me.parent)
        os.chdir(me.parent.parent.parent / "docker/volume.reader/")
    print(f"saving to {os.getcwd()}")

    signal.signal(signal.SIGTERM, _sigterm)
    pid_dicts = []

    swipe = UCFID()
    swipe.connect()

    try:
        swipe.listen()
    except KeyboardInterrupt:
        pass
    finally:
        save()
        # TODO backup local logs to some cloud platform (probably GCP or DB)
        print("Done collecting.")
