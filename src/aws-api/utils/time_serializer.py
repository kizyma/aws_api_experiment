import calendar
from datetime import datetime, timezone


# Timedata format & conversion is subject to change and might be easily changed as per request
# For now, I`m leaving these "as is", since I have no info on what proper DT structure is needed


def convert_datetime_to_iso_8601_with_z_suffix(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def transform_to_utc_datetime(dt: datetime) -> datetime:
    return dt.astimezone(tz=timezone.utc)


def convert_string_to_dt_object(datetime_str) -> datetime:
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S').astimezone(tz=timezone.utc)


# Decided NOT to include timestamp into basic data structure because I am not sure it will be necessary
# and it is dynamoDB aux. data structure anyway
def utc_timestamp(end_datetime) -> int:
    if type(end_datetime) is str:
        end_datetime = convert_string_to_dt_object(end_datetime)
    current_timetuple = end_datetime.utctimetuple()
    current_timestamp = calendar.timegm(current_timetuple)
    return current_timestamp
