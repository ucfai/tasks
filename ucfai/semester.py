import datetime
import json
from collections import namedtuple
from datetime import (
    time as Time
)

import pandas as pd
import requests
import yaml

from .attendance import Attendance
from .coordinator import Coordinator

obs_holidays = {
    "spring": ["Spring Break", "Martin Luther King Jr. Day", ],
    "fall"  : ["Veterans Day", "Labor Day", "Thanksgiving", ],
}

Meeting = namedtuple("Meeting", ["name", "cover", "coordinator", "description"])
MeetingInfo = namedtuple("MeetingInfo", ["date", "time_s", "time_e", "room"])

class Semester:
    def __init__(self):
        # self.overhead = self._parse_overhead()
        self.syllabus = self._parse_syllabus()

        self.shortened = ""
        self._parse_ucf_calendar()
        raise NotImplementedError()

    def _parse_syllabus(self):
        syllabus = yaml.load(open("syllabus.yml", "r"))
        assert type(syllabus) is list, \
            f"Syllabus is a {type(syllabus)}, not {type([])}. :/"

        meetings = []
        for meeting in syllabus:
            nb_name = NotebookName(meeting["name"], meeting["file"])
            meeting = Meeting(nb_name, meeting["covr"],
                              self.__coordinator_lookup(meeting["inst"]),
                              meeting["desc"])
            meetings.append(meeting)

        raise NotImplementedError()

    def _write_syllabus(self):
        raise NotImplementedError()

    def _parse_management(self):
        overhead_expected_keys = {"coordinators", "meetings"}
        overhead = yaml.load(open("overhead.yml", "r"))

        assert overhead_expected_keys.intersection(set(overhead.keys())) \
                is overhead_expected_keys

        coordinators = overhead["coordinators"]
        self.coordinators = [Coordinator(**c) for c in coordinators]

        meeting_info = overhead["meetings"]

        time_split = meeting_info["time"].split("-")
        time_err = ("Invalid time spec: use `<start>-<end>`; also, it should "
                    "be military time.")
        assert len(time_split) == 2, time_err
        meeting_info["time_s"] = Time(*time_split[0].split(":"))
        meeting_info["time_e"] = Time(*time_split[1].split(":"))

        raise NotImplementedError()

    def _write_management(self):
        raise NotImplementedError()

    def _make_attendance_forms(self) -> Attendance:
        raise NotImplementedError()

    def _parse_ucf_calendar(self) -> None:
        year, semester, self.shortened = which()
        holidays = obs_holidays[semester]
        ucf_cal_url = f"{calendar_ucf_url}/json/{year}/{semester}"

        ucf_calendar = requests.get(ucf_cal_url)
        ucf_cal_parse = json.loads(ucf_calendar.text)["term"]
        df_ucf_cal = pd.DataFrame.from_dict(ucf_cal_parse)

        starts = df_ucf_cal.loc[df_ucf_cal["summary"] == "Classes Begin"]
        finish = df_ucf_cal.loc[df_ucf_cal["summary"] == "Study Day"]

        # e.g. 2019-04-23 00:00:00Z -> yr=2019, mo=4, day=23, hr=0, min=0, sec=0
        def parse_ucf_date(dtstart: str, dtend: str = ""):
            st = datetime.strptime(dtstart, "%Y-%m-%d %H:%M:%SZ")
            if not dtend:
                return st
            return (st, datetime.strptime(dtend, "%Y-%m-%d %H:%M:%SZ"))

        starts_date = parse_ucf_date(starts["dtstart"])
        finish_date = parse_ucf_date(finish["dtstart"])

        select_holidays = df_ucf_cal.loc[df_ucf_cal["summary"].isin(holidays)]
        holidays = [parse_ucf_date(hol["dtstart"], hol["dtend"])
                    for hol in select_holidays]

        return starts_date, finish_date, holidays

    def __coordinator_lookup(self, param):
        pass


calendar_ucf_url = "https://calendar.ucf.edu"

def which():
    current_url = requests.get(calendar_ucf_url).url
    current_date = datetime.now()
    if current_date.month in [0, 7, 11]: # May, Aug, Dec (0-based)
        # this generates a URL like... https://calendar.ucf.edu/json/2018/fall
        # such a URL is necessary to snag the JSON object, which we can operate
        # on to figure out when "Class Begin" and "Study Day" are.
        if current_url.endswith("fall") and current_date.month == 11:
            current_url = current_url.replace(str(current_date.year),
                                              str(current_date.year + 1))
            current_url = current_url.replace("fall", "spring")
        elif current_url.endswith("summer"):
            current_url = current_url.replace("summer", "fall")

    print(current_url)

    year, semester = current_cal.replace(f"{calendar_ucf_url}/json", "").split("/")
    shortened = semester[:2] + year[2:]

    return year, semester, shortened