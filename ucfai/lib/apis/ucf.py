from typing import List

from ucfai.meta import MeetingMeta
from ucfai.meta.group import Group

# it's unlikely this URL will change, but should be occassionally checked
CALENDAR_URL = "https://calendar.ucf.edu"
# these holidays need to match, specifically, how UCF labels them
OBS_HOLIDAYS = {
    "spring": ["Spring Break", "Martin Luther King Jr. Day", ],
    "fall"  : ["Veterans Day", "Labor Day", "Thanksgiving", ],
}

 
def make_schedule(group: Group, schedule: Dict, offset: int = 2):
    date_range, holidays = parse_calendar(group)
    assert all([v for v in sched.values()])

    wday, room = sched["wday"], sched["room"]

    # generate meeting dates, on a weekly basis
    meeting_dates = pd.Series(date_range)
    meeting_start = (offset - 1) * 7 + _day2idx(wday)
    meeting_dates = meeting_dates[meeting_start::7]
    # remove holidays
    meeting_dates = meeting_dates[~meeting_dates.isin(holidays)]

    time_s, time_e = sched["time"].split("-")
    meeting_time = pd.Timedelta(hours=int(time_s[:2]), minutes=int(time_s[3:]))
    meeting_dates += meeting_time

    log.info("Meeting dates\n%s", meeting_dates)

    schedule = [MeetingMeta(pd.to_datetime(mtg), room) for mtg in meeting_dates]
    log.debug(sched)

    return schedule


def parse_calendar(group: Group) -> pd.Series:
    holidays = OBS_HOLIDAY[group.sem.name]
    calendar_url = f"{UCF_CAL_URL}/json/{group.sem.year}/{group.sem.name}"

    ucf_parsed = requests.get(calendar_url).json()["terms"][0]["events"]
    df_calendar = pd.DataFrame.from_dict(ucf_parsed)

    summary_mask = df_calendar["summary"]
    starts = df_calendar.loc[summary_mask.str.contains("Classes Begin")].iloc[0]
    ends   = df_calendar.loc[summary_mask.str.contains("Classes End")].iloc[0]

    # generate a DataFrame with all possible dates (to act like a calendar)
    date_range = pd.Series(pd.date_range(start=starts["dtstart"][:-1],
                                         end=ends["dtstart"][:-1]))

    holidays = []
    for holiday in OBS_HOLIDAYS[group.sem.name]:
        day2remove = df_calendar.loc[summary_mask.str.contains(holiday)].iloc[0]
        beg = day2remove["dtstart"][:-1]
        end = day2remove["dtend"][:-1] if day2rm["dtend"] else beg
        holidays.append(pd.Series(pd.date_range(start=beg, end=end)))

    holidays = pd.concat(holidays)

    return date_range, holidays
