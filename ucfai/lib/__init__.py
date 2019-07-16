UCF_CAL_URL = "https://calendar.ucf.edu"

OBS_HOLIDAY = {
    "spring": ["Spring Break", "Martin Luther King Jr. Day", ],
    "fall"  : ["Veterans Day", "Labor Day", "Thanksgiving", ],
}

from ucfai.tooling.ops import ACCEPTED_OPS

__all__ = ["UCF_CAL_URL", "OBS_HOLIDAY", "ACCEPTED_OPS", "ops", "apis"]
