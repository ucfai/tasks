from collections import OrderedDict
from datetime import datetime
from typing import Dict
import calendar

import pandas as pd
import requests

from .. import Group, Semester

# it's unlikely this URL will change, but should be occassionally checked
CALENDAR_URL = "https://calendar.ucf.edu"
# these holidays need to match, specifically, how UCF labels them
OBS_HOLIDAYS = {
    "spring": ["Spring Break", "Martin Luther King Jr. Day"],
    "summer": [],
    "fall": ["Veterans Day", "Labor Day", "Thanksgiving"],
}

# NOTE make sure to consider 0-indexing here
SEMESTER_LEN = {"spring": 14, "summer": 10, "fall": 15}
# this fixes off-by-1 errors __on the assumption__ we stop meetings the week before
#   finals begin.
SEMESTER_LEN = {k: v - 1 for k, v in SEMESTER_LEN.items()}


def temp_schedule(group: Group):
    return make_schedule(group, {})


def make_schedule(group: Group, schedule: Dict):
    date_range, holidays = parse_calendar(group)

    # on average, we've had 10 meetings per semester in the past
    # typically, we've started group meetings in the 3rd week of the semester
    offset = schedule.get("start_offset", 3)

    # Try to get the weekday's numeric value. If "wday" hasn't been specified
    #   (or isn't a 3-letter weekday acronym), then return a blank date-list with
    #   some assumptions based on prior meeting schedules.
    try:
        wday = list(calendar.day_abbr).index(schedule["wday"].capitalize())
    except (KeyError, ValueError):
        return [None] * (SEMESTER_LEN[group.semester.name.lower()] - offset)

    # Assume a once-a-week meeting basis and build the schedule accordingly.
    meeting_dates = pd.Series(date_range)
    meeting_start = offset * 7 + wday
    meeting_dates = meeting_dates[meeting_start::7]

    # Removes Holidays, if the array is non-empty.
    if holidays is not None:
        meeting_dates = meeting_dates[~meeting_dates.isin(holidays)]

    time_s, time_e = schedule["time"].split("-")
    meeting_time = pd.Timedelta(hours=int(time_s[:2]), minutes=int(time_s[2:]))
    meeting_dates += meeting_time

    schedule = [pd.to_datetime(mtg) for mtg in meeting_dates]

    return schedule


def parse_calendar(group: Group) -> tuple:
    holidays = OBS_HOLIDAYS[group.semester.name.lower()]

    # This is the URL for the calendar's JSON-based API. This will vary by institution.
    calendar_url = (
        f"{CALENDAR_URL}/json/{group.semester.year}/{group.semester.name.lower()}"
    )

    # UCF's JSON object holds all the "events" in an "events" identifier
    ucf_parsed = requests.get(calendar_url).json()["terms"][0]["events"]
    df_calendar = pd.DataFrame.from_dict(ucf_parsed)

    # The "summary" column of the new DataFrame holds the names of the events
    summary_mask = df_calendar["summary"]
    # Events are stored as arrays. It's easier to parse this way than reducing
    #   the list-containing column to something that isn't.
    starts = df_calendar.loc[summary_mask.str.contains("Classes Begin")].iloc[0]
    ends = df_calendar.loc[summary_mask.str.contains("Classes End")].iloc[0]

    # generate a DataFrame with all possible dates (to act like a calendar)
    date_range = pd.Series(
        pd.date_range(start=starts["dtstart"][:-1], end=ends["dtstart"][:-1])
    )

    # Remove the Holidays, since we assume students won't meet on those days.
    holidays = []
    for holiday in OBS_HOLIDAYS[group.semester.name]:
        day2remove = df_calendar.loc[summary_mask.str.contains(holiday)].iloc[0]
        beg = day2remove["dtstart"][:-1]
        end = day2remove["dtend"][:-1] if day2remove["dtend"] else beg
        holidays.append(pd.Series(pd.date_range(start=beg, end=end)))

    # Checking array nullity requires "... is not None" rather than ducktyping
    if holidays is not None:
        holidays = pd.concat(holidays)

    return date_range, holidays


def determine_semester() -> Semester:
    """Infers the current semester based on today's date.

    Takes advantage of the redirection https://ucf.calendar.edu/ has built-in.
    """
    current_url = requests.get(CALENDAR_URL).url
    current_date = datetime.now()

    may, aug, dec = [5, 8, 12]  # May, Aug, Dec (1-indexed)

    semester_dict = OrderedDict({"spring": may, "summer": aug, "fall": dec})

    semester_list = list(semester_dict.keys())
    n_semesters = len(semester_list)

    for idx, (semester, month) in enumerate(semester_dict.items()):
        if current_url.endswith(semester) and current_date.month == month:
            next_semester = semester_list[(idx + 1) % n_semesters]
            current_url = current_url.replace(semester, next_semester)

            if semester == "fall":  # increment the year as well
                year = current_date.year
                current_url = current_url.replace(f"{year}", f"{year + 1}")

    year, name = current_url.replace(f"{CALENDAR_URL}/", "").split("/")

    return Semester(name=name, year=year)
