import calendar
from pydantic import BaseModel, validator
from datetime import datetime, timezone, timedelta
from typing import Optional


# Timedata format & conversion is subject to change and might be easily changed as per request
# For now, I`m leaving these "as is", since I have no info on what proper DT structure is needed


# def convert_datetime_to_iso_8601_with_z_suffix(dt: datetime) -> str:
#     return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


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


class GenericEvent(BaseModel):
    # In this particular case only necessary data for user to provide - is event_id
    # This was made for two reasons - it is much easier to create valid test data this way,
    # and I am not really sure whether user provides API with all data all the time.

    event_name: Optional[str] = ''
    start_date: Optional[datetime] = ''
    end_date: Optional[datetime] = ''
    status: Optional[str] = ''
    event_id: int

    # custom input conversion for certain field
    _normalize_start_date = validator(
        "start_date",
        allow_reuse=True)(transform_to_utc_datetime)

    _normalize_end_date = validator(
        "end_date",
        allow_reuse=True)(transform_to_utc_datetime)

    class Config:
        json_encoders = {
            # custom output conversion for datetime
            datetime: convert_string_to_dt_object
        }

        validate_assignment = True

    # Following code won't be used on prod, unless such functionality is needed.
    # It is somewhat resource-consuming.
    # Decorators with default values setters
    @validator('status', pre=True, always=True)
    def set_event_status(cls, status):
        placeholder_status = 'completed'
        return status or placeholder_status

    @validator('event_name', pre=True, always=True)
    def set_event_name(cls, name):
        placeholder_event_name = 'Generic Test Event'
        return name or placeholder_event_name

    @validator('start_date', pre=True, always=True)
    def set_start_date(cls, start_date):
        generic_start_time = datetime.now() - timedelta(hours=1)
        return start_date or generic_start_time.astimezone(tz=timezone.utc)

    @validator('end_date', pre=True, always=True)
    def set_end_date(cls, end_date):
        generic_end_time = datetime.now()
        return end_date or generic_end_time.astimezone(tz=timezone.utc)
