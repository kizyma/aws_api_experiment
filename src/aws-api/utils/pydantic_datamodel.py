from pydantic import BaseModel, validator
from datetime import datetime, timezone, timedelta
from typing import Optional


def convert_datetime_to_iso_8601_with_z_suffix(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def transform_to_utc_datetime(dt: datetime) -> datetime:
    return dt.astimezone(tz=timezone.utc)


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

    _normalize_start_date = validator(
        "end_date",
        allow_reuse=True)(transform_to_utc_datetime)

    class Config:
        json_encoders = {
            # custom output conversion for datetime
            datetime: convert_datetime_to_iso_8601_with_z_suffix
        }
        validate_assignment = True

    # Decorators with default values setters
    @validator('status')
    def set_event_status(cls, status):
        return status or 'completed'

    @validator('event_name')
    def set_event_name(cls, name):
        return name or 'Generic Test Event'

    @validator('start_date')
    def set_start_date(cls, start_date):
        generic_start_time = datetime.now() - timedelta(hours=1)
        return start_date or generic_start_time

    @validator('end_date')
    def set_end_date(cls, end_date):
        generic_end_time = datetime.now()
        return end_date or generic_end_time
